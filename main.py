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


# ─── Home ─────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


# ─── Assessment ───────────────────────────────────────────────────────────────

@app.get("/assess/start")
async def start_assessment():
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = {"responses": {}, "started_at": datetime.utcnow().isoformat()}
    return RedirectResponse(f"/assess/{session_id}/1", status_code=303)


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
    db.save_profile(session_id, responses, profile_dict)

    del SESSIONS[session_id]

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


@app.get("/results/{session_id}/pdf")
async def download_pdf(session_id: str):
    profile_data = db.get_profile(session_id)
    if not profile_data:
        raise HTTPException(404, "Profile not found")

    profile = json.loads(profile_data["profile_json"])
    pdf_bytes = generate_pdf_report(profile, session_id)

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


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
