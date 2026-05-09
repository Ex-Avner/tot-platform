"""
TOT Research Platform — Web Application
Triaxial Orientation Theory by Ross Erickson / Avner Media
"""

import os
import uuid
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import anthropic
import resend
import uvicorn

# Engine imports
import sys
sys.path.insert(0, str(Path(__file__).parent))
from engine.tot_engine import TOTEngine, TOTScorer
from engine.tot_items import (
    get_item_bank, get_item_pole_map, get_integration_item_ids,
    get_hom_item_ids, get_reverse_coded_ids, OHN_ITEMS, HOC_ITEMS, HIM_ITEMS,
    ALLMEN_ITEMS, WASONCE_ITEMS, WILLBE_ITEMS, INTEGRATION_ITEMS, HOM_ITEMS
)
from database import TOTWebDB
from report import generate_pdf_report

app = FastAPI(title="TOT Research Platform", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

db = TOTWebDB()
engine = TOTEngine()
scorer = TOTScorer()

# In-memory session store: session_id -> {responses: {}, started_at: str}
SESSIONS: dict = {}

COACH_PASSWORD = os.getenv("TOT_COACH_PASSWORD", "avner2025")

SECTIONS = [
    {"key": "ohn",      "title": "Depth",           "subtitle": "Your relationship to what lies beneath the surface of experience", "questions": OHN_ITEMS},
    {"key": "hoc",      "title": "Surface",          "subtitle": "Your relationship to the immediate, practical, and concrete",     "questions": HOC_ITEMS},
    {"key": "him",      "title": "Singular Self",    "subtitle": "Your relationship to your own independent perspective",           "questions": HIM_ITEMS},
    {"key": "allmen",   "title": "Collective Other", "subtitle": "Your relationship to other people and shared experience",        "questions": ALLMEN_ITEMS},
    {"key": "wasonce",  "title": "Ancestral Past",   "subtitle": "Your relationship to what came before you",                     "questions": WASONCE_ITEMS},
    {"key": "willbe",   "title": "Unborn Future",    "subtitle": "Your relationship to what comes after you",                     "questions": WILLBE_ITEMS},
    {"key": "integration", "title": "Integration",  "subtitle": "How your orientations hold together under pressure",             "questions": INTEGRATION_ITEMS},
    {"key": "hom",         "title": "Interpretive Orientation", "subtitle": "How you relate to your own understanding of yourself", "questions": HOM_ITEMS},
]


APP_URL = os.getenv("APP_URL", "")


def _send_report_email(to_email: str, display_name: str, pdf_bytes: bytes, session_id: str) -> tuple:
    api_key = os.getenv("RESEND_API_KEY", "")
    if not api_key:
        return False, "Email service not configured"
    from_addr = os.getenv("REPORT_FROM_EMAIL", "TOT Research <onboarding@resend.dev>")
    resend.api_key = api_key
    name_line = f"Hello {display_name}," if display_name else "Hello,"
    results_url = f"{APP_URL}/results/{session_id}" if APP_URL else ""
    link_html = f'<p>View your interactive results online: <a href="{results_url}">{results_url}</a></p>' if results_url else ""
    try:
        resend.Emails.send({
            "from": from_addr,
            "to": [to_email],
            "subject": f"Your TOT Orientation Profile",
            "html": f"""
                <div style="font-family:sans-serif;max-width:600px;margin:0 auto;background:#0b1021;color:#e8ecf5;padding:32px;border-radius:8px;">
                  <h2 style="color:#5eead4;margin-top:0;">Triaxial Orientation Theory</h2>
                  <p>{name_line}</p>
                  <p>Your full Orientation Profile is attached as a PDF.</p>
                  {link_html}
                  <p style="color:#9fb0c5;font-size:12px;margin-top:40px;">
                    Triaxial Orientation Theory — Ross Erickson / Avner Media<br>
                    Pre-validation research instrument
                  </p>
                </div>
            """,
            "attachments": [{
                "filename": f"TOT_Profile_{session_id[:8].upper()}.pdf",
                "content": list(pdf_bytes),
            }],
        })
        return True, "Sent"
    except Exception as e:
        return False, str(e)


# ─── Home ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# ─── Consent ──────────────────────────────────────────────────────────────────

@app.get("/assess/consent", response_class=HTMLResponse)
async def consent_page(request: Request):
    return templates.TemplateResponse("consent.html", {"request": request})


@app.post("/assess/consent/start")
async def consent_start(
    request: Request,
    display_name: str = Form(""),
    email: str = Form(""),
    consented: str = Form(""),
):
    if not consented:
        return templates.TemplateResponse("consent.html", {
            "request": request,
            "error": "You must consent to proceed.",
            "display_name": display_name,
            "email": email,
        })
    if not display_name.strip():
        return templates.TemplateResponse("consent.html", {
            "request": request,
            "error": "Please enter your name or initials.",
            "email": email,
        })
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {
        "responses": {},
        "started_at": datetime.utcnow().isoformat(),
        "display_name": display_name.strip(),
        "email": email.strip(),
        "consented": True,
    }
    return RedirectResponse(f"/assess/{session_id}/1", status_code=303)


# ─── Assessment ───────────────────────────────────────────────────────────────

@app.get("/assess/start")
async def start_assessment():
    return RedirectResponse("/assess/consent", status_code=303)


@app.get("/assess/{session_id}/submit", response_class=HTMLResponse)
async def submit_assessment(request: Request, session_id: str):
    if session_id not in SESSIONS:
        return RedirectResponse("/", status_code=303)

    session = SESSIONS[session_id]
    responses = session["responses"]

    if len(responses) < 66:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": f"Assessment incomplete — {len(responses)}/72 items answered. Please go back and complete all sections.",
        })

    item_pole_map = get_item_pole_map()
    integration_ids = get_integration_item_ids()
    hom_ids = get_hom_item_ids()
    reverse_ids = get_reverse_coded_ids()

    poles = scorer.score_likert_responses(responses, item_pole_map)
    integration_scores = scorer.score_integration_items(responses, integration_ids, reverse_ids)
    hom_scores = [
        (responses[iid] - 1) / 6.0
        for iid in hom_ids if iid in responses
    ]
    profile = engine.compute_profile(poles, integration_scores, hom_scores=hom_scores, participant_id=session_id)

    profile_dict = profile.to_dict()
    display_name = session.get("display_name", "")
    email = session.get("email", "")

    db.save_profile(session_id, responses, profile_dict, display_name=display_name)
    del SESSIONS[session_id]

    if email:
        try:
            pdf_bytes = generate_pdf_report(profile_dict, session_id, display_name=display_name)
            _send_report_email(email, display_name, pdf_bytes, session_id)
        except Exception:
            pass

    return RedirectResponse(f"/results/{session_id}", status_code=303)


@app.get("/assess/{session_id}/{section_num}", response_class=HTMLResponse)
async def assessment_section(request: Request, session_id: str, section_num: int):
    if session_id not in SESSIONS:
        return RedirectResponse("/", status_code=303)
    if section_num < 1 or section_num > len(SECTIONS):
        return RedirectResponse("/", status_code=303)

    section = SECTIONS[section_num - 1]
    existing = SESSIONS[session_id]["responses"]
    total_sections = len(SECTIONS)
    progress = round((section_num - 1) / total_sections * 100)

    return templates.TemplateResponse("assessment.html", {
        "request": request,
        "session_id": session_id,
        "section": section,
        "section_num": section_num,
        "total_sections": total_sections,
        "progress": progress,
        "existing_responses": existing,
        "is_last": section_num == total_sections,
    })


@app.post("/assess/{session_id}/{section_num}/save")
async def save_section(request: Request, session_id: str, section_num: int):
    if session_id not in SESSIONS:
        raise HTTPException(404, "Session not found")

    form = await request.form()
    for key, value in form.items():
        if key.startswith(("V", "H", "T", "I")):
            try:
                SESSIONS[session_id]["responses"][key] = int(value)
            except ValueError:
                pass

    if section_num < len(SECTIONS):
        return RedirectResponse(f"/assess/{session_id}/{section_num + 1}", status_code=303)
    else:
        return RedirectResponse(f"/assess/{session_id}/submit", status_code=303)


# ─── Results ──────────────────────────────────────────────────────────────────

@app.get("/results/{session_id}", response_class=HTMLResponse)
async def results(request: Request, session_id: str):
    profile_data = db.get_profile(session_id)
    if not profile_data:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Profile not found. Please take the assessment first.",
        })

    profile = json.loads(profile_data["profile_json"])
    return templates.TemplateResponse("results.html", {
        "request": request,
        "session_id": session_id,
        "profile": profile,
        "profile_json": json.dumps(profile),
    })


@app.post("/results/{session_id}/send-email")
async def send_email_report(request: Request, session_id: str):
    profile_data = db.get_profile(session_id)
    if not profile_data:
        raise HTTPException(404, "Profile not found")
    body = await request.json()
    email = (body.get("email") or "").strip()
    if not email or "@" not in email:
        return {"ok": False, "error": "Invalid email address"}
    profile = json.loads(profile_data["profile_json"])
    display_name = profile_data.get("display_name", "")
    pdf_bytes = generate_pdf_report(profile, session_id, display_name=display_name)
    ok, msg = _send_report_email(email, display_name, pdf_bytes, session_id)
    return {"ok": ok, "error": "" if ok else msg}


@app.get("/results/{session_id}/pdf")
async def download_pdf(session_id: str):
    profile_data = db.get_profile(session_id)
    if not profile_data:
        raise HTTPException(404, "Profile not found")

    profile = json.loads(profile_data["profile_json"])
    display_name = profile_data.get("display_name", "")
    pdf_bytes = generate_pdf_report(profile, session_id, display_name=display_name)

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=TOT_Profile_{session_id[:8]}.pdf"}
    )


# ─── Coach Dashboard ──────────────────────────────────────────────────────────

def verify_coach(request: Request):
    auth = request.cookies.get("coach_auth")
    if auth != COACH_PASSWORD:
        raise HTTPException(401)


@app.get("/coach/login", response_class=HTMLResponse)
async def coach_login_page(request: Request):
    return templates.TemplateResponse("coach_login.html", {"request": request})


@app.post("/coach/login")
async def coach_login(password: str = Form(...)):
    if password != COACH_PASSWORD:
        return RedirectResponse("/coach/login?error=1", status_code=303)
    response = RedirectResponse("/coach", status_code=303)
    response.set_cookie("coach_auth", password, httponly=True)
    return response


@app.get("/coach", response_class=HTMLResponse)
async def coach_dashboard(request: Request):
    if request.cookies.get("coach_auth") != COACH_PASSWORD:
        return RedirectResponse("/coach/login", status_code=303)

    profiles = db.get_all_profiles()
    stats = db.get_stats()
    return templates.TemplateResponse("coach.html", {
        "request": request,
        "profiles": profiles,
        "stats": stats,
    })


@app.get("/coach/client/{session_id}", response_class=HTMLResponse)
async def coach_client(request: Request, session_id: str):
    if request.cookies.get("coach_auth") != COACH_PASSWORD:
        return RedirectResponse("/coach/login", status_code=303)

    profile_data = db.get_profile(session_id)
    if not profile_data:
        raise HTTPException(404, "Client not found")

    profile = json.loads(profile_data["profile_json"])
    return templates.TemplateResponse("results.html", {
        "request": request,
        "session_id": session_id,
        "profile": profile,
        "profile_json": json.dumps(profile),
        "coach_view": True,
    })


def _build_profile_summary(profile: dict) -> str:
    axes = profile.get("axis_scores", {})
    geo = profile.get("geometry", {})
    hom = profile.get("hall_of_mirrors", {})
    poles = profile.get("pole_scores", {})

    lines = [
        f"Zone: {profile.get('zone', 'Unknown')}",
        f"Primary Subtype: {profile.get('primary_subtype', '')} — {profile.get('subtype_description', '')}",
        f"Shape Parameter: {profile.get('shape_parameter', 1.0):.3f} ({profile.get('shape_name', '')})",
        f"",
        f"Axis Scores:",
        f"  Vertical (Depth ↔ Surface): {axes.get('vertical', 0):+.3f}",
        f"  Horizontal (Singular ↔ Collective): {axes.get('horizontal', 0):+.3f}",
        f"  Temporal Extension: {axes.get('temporal_extension', 0):.3f}",
        f"  Temporal Balance (Past ↔ Future): {axes.get('temporal_balance', 0):+.3f}",
        f"",
        f"Pole Scores (0–1):",
    ]
    for pole, score in poles.items():
        lines.append(f"  {pole}: {score:.3f}")

    lines += [
        f"",
        f"Geometric Detail:",
        f"  Weakest Axis: {geo.get('weakest_axis', '')}",
        f"  Strongest Axis: {geo.get('strongest_axis', '')}",
        f"  Axis Imbalance: {geo.get('axis_imbalance', 0):.3f}",
        f"  Self-Reported Integration (p): {geo.get('p_self_report', 1.0):.3f}",
        f"  Empirical Integration (p): {geo.get('p_empirical', 1.0):.3f}",
        f"  Deformations: {', '.join(geo.get('deformations', [])) or 'None'}",
        f"",
        f"Capture: {profile.get('capture_type', 'None')} — {profile.get('capture_primary', '')}",
        f"Primary Intergenerational Stamp: {profile.get('primary_stamp', 'None')}",
        f"",
        f"Hall of Mirrors (9th Formation): {'DETECTED' if hom.get('detected') else 'Not detected'} (score {hom.get('score', 0):.3f})",
    ]
    return "\n".join(lines)


TOT_SYSTEM_PROMPT = """You are an interpreter of Triaxial Orientation Theory (TOT), a geometric psychometric framework developed by Ross Erickson. You are speaking directly with someone who has just completed the TOT assessment.

TOT maps psychological orientation across three axes:
- Vertical (Depth): Ohn pole (depth, ground of being, contact with what underlies experience) vs. Hoc pole (surface, immediate, practical, measurable)
- Horizontal (Breath): Him pole (singular self, epistemic independence, holds its own position) vs. Allmen pole (collective other, community, genuinely changed by others)
- Temporal (Obligation): Wasonce pole (ancestral past, inherited obligation, what came before) vs. Willbe pole (unborn future, obligation to what comes after)

The shape parameter (Lp norm) describes integration capacity — how well the person holds multiple orientations simultaneously. Low p (below 1.0) indicates crisis geometry — contact with one axis collapses the others. High p (above 2.0) indicates genuine multi-axis capacity.

The eight zones are positions within octahedral space. The Hall of Mirrors (9th formation) is NOT a zone — it is a collapse inward through self-referential epistemic closure. The person references all orientations through a recursive self-model without making genuine contact with any pole.

Stamps are intergenerational geometric deformations — inherited patterns from previous generations that compress or fracture the octahedral space.

Speak directly with this person. Be honest, specific, and personal — not clinical. Do not produce bullet point lists. Do not explain the theory abstractly unless they ask. Connect their orientation profile to the concrete patterns of an actual human life. When something in the profile is significant, name it plainly. Ask questions when you need to understand their situation better. You are not a therapist — you are someone who genuinely understands this framework and is willing to help them think about what it reveals about their path.

This person's profile:
{PROFILE_SUMMARY}"""


@app.post("/results/{session_id}/chat")
async def chat(request: Request, session_id: str):
    profile_data = db.get_profile(session_id)
    if not profile_data:
        raise HTTPException(404, "Profile not found")

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "REPLACE_WITH_YOUR_KEY":
        async def no_key():
            yield "Chat is not yet configured. The platform owner needs to add an Anthropic API key."
        return StreamingResponse(no_key(), media_type="text/plain")

    body = await request.json()
    messages = body.get("messages", [])
    if not messages:
        raise HTTPException(400, "No messages provided")

    profile = json.loads(profile_data["profile_json"])
    summary = _build_profile_summary(profile)
    system_prompt = TOT_SYSTEM_PROMPT.replace("{PROFILE_SUMMARY}", summary)

    client = anthropic.Anthropic(api_key=api_key)

    def stream_response():
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text

    return StreamingResponse(stream_response(), media_type="text/plain")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
