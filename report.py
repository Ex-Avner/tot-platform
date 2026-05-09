"""
TOT Report Generator — Comprehensive PDF with plain-English interpretation.
"""

import io
from datetime import datetime
from typing import Dict


# ── Plain-English interpretation content ─────────────────────────────────────

ZONE_SUMMARIES = {
    "Zone I: The Performer": (
        "The Performer operates at high capacity in the immediate and concrete. "
        "The orientation is surface-dominant, singular, and present-locked — "
        "meaning depth, community, and temporal obligation are not active registers. "
        "Function is high. Meaning is thin. The Performer can produce exceptional output "
        "without a clear answer to why it matters. This is not a failure of intelligence "
        "or effort — it is a structural condition. The axes that carry significance are "
        "largely offline."
    ),
    "Zone II: The Crowd": (
        "The Crowd is socially active, surface-dominant, and present-locked. "
        "Connection to other people is real and immediate, but it is not anchored "
        "in depth or in time. The orientation moves with whoever is in the room. "
        "Community is present but diffuse — the kind that assembles easily and "
        "disperses without leaving much behind. There is genuine warmth here, "
        "and a real responsiveness to others. What is missing is a root."
    ),
    "Zone III: The Mystic": (
        "The Mystic has genuine contact with depth — with what lies beneath the surface "
        "of ordinary experience. This contact is real and direct, not theoretical. "
        "But it occurs in isolation. The horizontal axis (community) and the temporal axis "
        "(past and future obligation) are not active. The depth does not connect outward "
        "or forward. The Mystic can see clearly and cannot bring anyone with them."
    ),
    "Zone IV: The Congregation": (
        "The Congregation holds depth and community simultaneously, but without temporal "
        "grounding. There is genuine spiritual or existential contact, and it is shared "
        "with others — this is not the isolation of the Mystic. But the past and future "
        "are not active registers. The community reinvents the wheel each generation "
        "because it has not yet connected its depth to the chain of time."
    ),
    "Zone V: The Archivist": (
        "The Archivist carries temporal obligation — both inherited and forward-facing — "
        "but does so alone and without depth contact. The past and future are real and "
        "active, but they are held at the surface level and without community. "
        "This is the lone ancestor-bearer: someone who knows what has been carried "
        "and what must be handed forward, doing the work in isolation, without access "
        "to what lies beneath it all."
    ),
    "Zone VI: The Tradition": (
        "The Tradition holds collective identity through time — community that carries "
        "history. This is the zone of cultural continuity: organizations, institutions, "
        "inherited practices. The connection to past and future is real, and it is shared. "
        "What is missing is depth. The form is maintained. The animating force "
        "beneath it has often departed."
    ),
    "Zone VII: The Prophet": (
        "The Prophet holds depth, temporal obligation, and epistemic independence "
        "simultaneously — and carries this largely alone. The orientation is toward "
        "something real and significant. The past and future are both active. "
        "The horizontal axis — community — is present but not dominant. "
        "The Prophet sees something others have not yet seen, and does the work "
        "of carrying it without the people to carry it with. This is a structurally "
        "isolating position. Not by choice, but by the geometry."
    ),
    "Zone VIII: The Somey": (
        "The Somey holds all three axes simultaneously — depth, community, and temporal "
        "obligation — and the shape geometry indicates these axes support rather than "
        "compete with each other. Depth does not cost community. Temporal obligation "
        "does not flatten the present. This is not a permanent state but a practiced one: "
        "something that must be continually returned to. The Somey is the zone of full "
        "orientation, and it requires ongoing maintenance. It is not achieved and held — "
        "it is practiced and re-entered."
    ),
}

SUBTYPE_NOTES = {
    "The Optimizer": "Peak performance has become a substitute for meaning. Output is high and direction is unclear.",
    "The Ghost": "Present in every room, absent from every experience. Functional dissociation.",
    "The Competitor": "Identity organized around opposition. The self exists primarily in contrast to something else.",
    "The Mirror": "Identity shifts to match whoever is present. The self is highly relational and unstable under solitude.",
    "The Influencer": "Audience as identity. Social presence has replaced interior life as the organizing structure.",
    "The Swarm": "Group identity without individual moral discernment. The collective is the self.",
    "The Hermit": "Genuine depth contact with total withdrawal from the horizontal. The interior is rich; the exterior is empty.",
    "The Psychonaut": "Depth accessed through altered states or intensity. Contact is real but not integrated.",
    "The Sage Trap": "Depth contact has become a source of hierarchy. Insight used as superiority.",
    "The Revival": "Communal spiritual intensity without historical grounding. Each gathering reinvents the wheel.",
    "The Circle": "Authentic community with genuine depth. Sealed. Does not export what it discovers.",
    "The Greenhouse": "Genuine transformation in a protected environment. What grows inside does not survive outside.",
    "The Burden-Bearer": "Carries generational weight alone. Cannot put it down. Cannot share it.",
    "The Historian": "Knows everything about what happened. Connected to none of it at depth.",
    "The Sentinel": "Watches the long-term consequences. Nobody is listening.",
    "The Custodian": "Maintains the form after the meaning has departed. Keeps the lights on in an empty building.",
    "The Monument": "Collective identity through heritage performance rather than living practice.",
    "The Institution": "Organizational memory without living purpose. Structure persists after the reason is gone.",
    "The Visionary": "Genuine sight with genuine isolation. Has the framework. Does not yet have the room.",
    "The Martyr": "Depth and obligation without community. Sacrificial by structure, not by choice.",
    "The Builder": "Creating the architecture nobody has been invited into yet.",
    "The Moment": "Temporary full orientation. Cannot be held. Can be recognized when it arrives.",
    "The Elder": "Sustained practice across all three axes. Never permanent. Always returning. This is not a fixed state — it is a practiced one.",
    "The Bridge": "Connects shards. Facilitates the assembly of what belongs together without directing it.",
}

STAMP_DESCRIPTIONS = {
    "Scarcity Stamp": (
        "The Scarcity Stamp reflects inherited resource deprivation — famine, poverty, or sustained "
        "material insecurity across generations. The orientation space was compressed before you arrived. "
        "Depth tends to register as luxury. Trust tends to register as risk. The past carries the weight "
        "of loss. This is not personal failure — it is inherited geometry."
    ),
    "Displacement Stamp": (
        "The Displacement Stamp reflects inherited exile, forced migration, or cultural severance. "
        "Belonging is complicated — not because of personal failure, but because the containers "
        "you were handed do not quite fit. There is often a pattern of building things that do not "
        "fit existing categories, and a difficulty finding the community that can hold what you carry. "
        "The severing happened before you did."
    ),
    "Violence Stamp": (
        "The Violence Stamp reflects sustained exposure to harm across generations. "
        "The horizontal axis — trust, community, genuine openness to others — "
        "carries evidence of fracture. Connection is possible but not unconditional. "
        "The past is monitored more than inhabited. This is a protective geometry "
        "that served a real purpose and may now be running at higher cost than the threat requires."
    ),
    "Silencing Stamp": (
        "The Silencing Stamp reflects inherited suppression of voice, truth, or identity. "
        "Depth is present but expressed through a filtered or indirect channel. "
        "There may be a pattern of knowing things you cannot say, or saying things "
        "that do not fully carry what you mean. The vertical axis is alive but not free."
    ),
    "Abandonment Stamp": (
        "The Abandonment Stamp reflects inherited patterns of relational loss — "
        "parental absence, repeated severing, the disappearance of people who mattered. "
        "Depth is accessible but tends to be unshared. Community is possible but "
        "carries an anticipation of loss. The recoil from genuine connection is not "
        "a character trait — it is an inherited orientation toward relational risk."
    ),
    "None": (
        "No single intergenerational stamp pattern reached the detection threshold. "
        "This indicates that the orientation profile does not strongly match any of the "
        "five known inherited deformation patterns. This does not mean inherited patterns "
        "are absent — only that none of the five measured profiles is dominant."
    ),
}

SHAPE_DESCRIPTIONS = {
    "Suboctahedron (Crisis)": (
        "The shape parameter below 0.8 indicates crisis geometry. Engaging one axis "
        "significantly collapses the others — when depth is active, community and temporal "
        "orientation tend to go offline, and vice versa. The interior space is constrained "
        "and angular. Holding multiple orientations simultaneously is genuinely costly."
    ),
    "Octahedron (Constrained)": (
        "The shape parameter near 1.0 indicates a constrained but functional geometry — "
        "the standard octahedron. Axis tradeoffs are linear: engaging depth costs community, "
        "and engaging community costs depth. The person can hold one orientation strongly "
        "at a time. Integration is possible but requires effort and tends not to be stable."
    ),
    "Rounded Octahedron (Functional)": (
        "The shape parameter between 1.2 and 1.8 indicates a rounded geometry — "
        "the axes have begun to support each other. Engaging depth does not fully cost "
        "community. Temporal orientation does not flatten the present. There is genuine "
        "multi-axis capacity here, though it is not yet effortless."
    ),
    "Sphere (Integrated)": (
        "The shape parameter near 2.0 indicates sphere geometry — genuine multi-axis "
        "integration. The axes support rather than compete with each other. Depth does "
        "not cost community. Temporal obligation does not collapse present engagement. "
        "This is not a permanent condition but a demonstrated structural capacity: "
        "the person has shown they can hold multiple orientations without one "
        "consuming the others."
    ),
    "Hyperround (Generative)": (
        "The shape parameter above 2.3 indicates hyperround geometry — the most integrated "
        "configuration. Holding all three axes simultaneously is not only possible but "
        "feels natural. The interior space is large and the orientations are mutually "
        "generative. This is rare and should be interpreted carefully alongside the "
        "pole scores: genuine hyperround capacity is demonstrated across all poles, "
        "not just self-reported."
    ),
}


def _generate_narrative(profile: Dict) -> list:
    """Generate plain-English interpretive paragraphs for this specific profile."""
    zone = profile.get("zone", "")
    subtype = profile.get("primary_subtype", "")
    axes = profile.get("axis_scores", {})
    poles = profile.get("pole_scores", {})
    geo = profile.get("geometry", {})
    shape = profile.get("shape_parameter", 1.0)
    shape_name = profile.get("shape_name", "")
    stamp = profile.get("primary_stamp", "None")
    capture = profile.get("capture_type", "No Capture")
    hom = profile.get("hall_of_mirrors", {})

    v = axes.get("vertical", 0)
    h = axes.get("horizontal", 0)
    t_ext = axes.get("temporal_extension", 0)
    t_bal = axes.get("temporal_balance", 0)

    ohn = poles.get("Ohn (Depth)", 0)
    hoc = poles.get("Hoc (Surface)", 0)
    him = poles.get("Him (Singular)", 0)
    allmen = poles.get("Allmen (Plural)", 0)
    wasonce = poles.get("Wasonce (Past)", 0)
    willbe = poles.get("Willbe (Future)", 0)

    paragraphs = []

    # ── Paragraph 1: Core orientation ────────────────────────────────────────
    p1_parts = []

    # Vertical axis
    if v < -0.5:
        p1_parts.append(
            f"The dominant orientation is depth. With an Ohn score of {ohn:.2f} "
            f"and Hoc at {hoc:.2f}, this profile lives primarily in the register "
            f"beneath ordinary surface experience — in what is fundamental, "
            f"foundational, and beneath the practical. The surface register "
            f"(immediate, concrete, transactional) is significantly underdeveloped "
            f"relative to the depth capacity."
        )
    elif v < -0.2:
        p1_parts.append(
            f"The orientation leans toward depth. Ohn ({ohn:.2f}) outpaces "
            f"Hoc ({hoc:.2f}), indicating a preference for what lies beneath "
            f"the surface of experience over the immediate and practical. "
            f"The surface register is present but secondary."
        )
    elif v > 0.5:
        p1_parts.append(
            f"The dominant orientation is surface — the immediate, practical, "
            f"and concrete. With Hoc at {hoc:.2f}, this profile is most active "
            f"in the register of what can be done, measured, and produced now. "
            f"The depth register (Ohn: {ohn:.2f}) is significantly less active."
        )
    elif v > 0.2:
        p1_parts.append(
            f"The orientation leans toward the surface — the practical and immediate. "
            f"Hoc ({hoc:.2f}) outpaces Ohn ({ohn:.2f}), indicating "
            f"a preference for the concrete and actionable over the foundational."
        )
    else:
        p1_parts.append(
            f"The vertical axis is near-balanced — Ohn ({ohn:.2f}) and "
            f"Hoc ({hoc:.2f}) are close in score, indicating the profile "
            f"can move between depth and surface without strong pull in either direction."
        )

    # Horizontal axis
    if h < -0.3:
        p1_parts.append(
            f"The horizontal axis is singular-dominant (Him: {him:.2f}, "
            f"Allmen: {allmen:.2f}). The orientation holds its own position "
            f"independently. Community is possible but not the primary register — "
            f"the epistemic center of gravity is internal."
        )
    elif h > 0.3:
        p1_parts.append(
            f"The horizontal axis is collective-dominant (Allmen: {allmen:.2f}, "
            f"Him: {him:.2f}). The orientation is genuinely affected by others "
            f"and draws meaning from community. The self is constituted in relation."
        )
    elif abs(h) <= 0.3 and him > 0.6 and allmen > 0.6:
        p1_parts.append(
            f"The horizontal axis is near-balanced with both poles elevated — "
            f"Him at {him:.2f} and Allmen at {allmen:.2f}. This indicates "
            f"genuine capacity for both independent position and community engagement. "
            f"The profile can hold its own ground and remain genuinely open to others."
        )

    paragraphs.append(" ".join(p1_parts))

    # ── Paragraph 2: Temporal and integration ────────────────────────────────
    p2_parts = []

    if t_ext > 0.8:
        if abs(t_bal) < 0.05:
            p2_parts.append(
                f"The temporal axis is fully extended and precisely balanced — "
                f"Wasonce ({wasonce:.2f}) and Willbe ({willbe:.2f}) are nearly identical. "
                f"This is an unusual configuration: the profile carries both inherited "
                f"obligation and future-directed obligation at the same weight simultaneously. "
                f"Past and future are both live and neither dominates."
            )
        elif t_bal > 0.2:
            p2_parts.append(
                f"The temporal axis is fully extended and future-leaning. "
                f"Willbe ({willbe:.2f}) outpaces Wasonce ({wasonce:.2f}). "
                f"Obligation runs primarily toward what comes after — "
                f"toward future generations and what will outlast the self."
            )
        else:
            p2_parts.append(
                f"The temporal axis is fully extended and past-leaning. "
                f"Wasonce ({wasonce:.2f}) outpaces Willbe ({willbe:.2f}). "
                f"Obligation runs primarily toward what came before — "
                f"toward inherited patterns, ancestral weight, and what was handed down."
            )
    elif t_ext > 0.5:
        p2_parts.append(
            f"The temporal axis is moderately active. Past and future are present "
            f"as real orientations but do not carry maximum load. "
            f"There is temporal range without full extension."
        )
    else:
        p2_parts.append(
            f"The temporal axis is largely collapsed. The profile is primarily "
            f"present-oriented — the past and future are not active registers. "
            f"Obligation runs to the immediate rather than across generations."
        )

    # Shape interpretation
    if shape >= 1.8:
        p2_parts.append(
            f"The shape parameter ({shape:.3f}, {shape_name}) indicates genuine "
            f"integration capacity — the axes support each other rather than compete. "
            f"Engaging depth does not cost community, and carrying temporal obligation "
            f"does not flatten present engagement."
        )
    elif shape >= 1.2:
        p2_parts.append(
            f"The shape parameter ({shape:.3f}, {shape_name}) indicates functional "
            f"but constrained integration. There is multi-axis capacity, though "
            f"engaging one axis does place some cost on the others."
        )
    else:
        p2_parts.append(
            f"The shape parameter ({shape:.3f}, {shape_name}) indicates constrained "
            f"integration. Engaging one axis places significant cost on the others — "
            f"depth, community, and temporal obligation tend to compete "
            f"rather than support each other."
        )

    paragraphs.append(" ".join(p2_parts))

    # ── Paragraph 3: Stamp and capture ───────────────────────────────────────
    p3_parts = []

    if stamp and stamp != "None":
        stamp_short = {
            "Scarcity Stamp": "inherited resource deprivation — the geometry was compressed before arrival",
            "Displacement Stamp": "inherited exile or severance — belonging has been structurally complicated across generations",
            "Violence Stamp": "inherited exposure to harm — the axis of trust and community carries evidence of fracture",
            "Silencing Stamp": "inherited suppression of voice or identity — depth is present but filtered",
            "Abandonment Stamp": "inherited relational loss — depth is accessible but community carries anticipation of severance",
        }
        p3_parts.append(
            f"The primary intergenerational stamp is {stamp} — "
            f"reflecting {stamp_short.get(stamp, 'an inherited deformation pattern')}. "
            f"This is not a pathology. It is a geometric inheritance: "
            f"orientation shaped by what was carried across generations before any choice was made."
        )

    if hom and hom.get("detected"):
        p3_parts.append(
            f"The Hall of Mirrors pattern was detected (score {hom.get('score', 0):.3f}). "
            f"This indicates a self-referential epistemic structure: the profile references "
            f"all orientations through an internal framework that tends to absorb new experience "
            f"rather than be revised by it. This is geometrically distinct from genuine integration — "
            f"it resembles integration from the outside while maintaining no direct contact with any pole."
        )

    if capture and capture != "No Capture":
        capture_primary = profile.get("capture_primary", "")
        intensity = profile.get("capture_intensity", 0)
        if capture == "Vertex Capture":
            p3_parts.append(
                f"A Vertex Capture ({capture_primary}, intensity {intensity:.2f}) is present. "
                f"Orientation has become strongly fixed toward a single pole. "
                f"The other five poles are significantly less active."
            )
        elif capture == "Edge Capture":
            p3_parts.append(
                f"An Edge Capture ({capture_primary}, intensity {intensity:.2f}) is present. "
                f"Orientation is fixed between two adjacent poles, with the remaining "
                f"four axes significantly less active."
            )

    if not p3_parts:
        p3_parts.append(
            "No dominant intergenerational stamp or capture pattern was detected above threshold. "
            "The profile does not show strong evidence of geometric inheritance or fixed capture."
        )

    paragraphs.append(" ".join(p3_parts))

    return paragraphs


# ── PDF Builder ───────────────────────────────────────────────────────────────

def generate_pdf_report(profile: Dict, session_id: str, display_name: str = "") -> bytes:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, KeepTogether, PageBreak
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    except ImportError:
        return _fallback_pdf(profile, session_id)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.75 * inch, bottomMargin=0.75 * inch,
                            leftMargin=inch, rightMargin=inch)

    DARK    = colors.HexColor("#0b1021")
    MINT    = colors.HexColor("#5eead4")
    SKY     = colors.HexColor("#38bdf8")
    MUTED   = colors.HexColor("#9fb0c5")
    TEXT    = colors.HexColor("#e8ecf5")
    PANEL   = colors.HexColor("#10182e")
    PANEL2  = colors.HexColor("#0f1c33")
    BORDER  = colors.HexColor("#1e2a42")
    WARM    = colors.HexColor("#f59e0b")

    def style(name, **kw):
        base = dict(fontName="Helvetica", fontSize=10, textColor=TEXT,
                    leading=14, spaceAfter=6)
        base.update(kw)
        return ParagraphStyle(name, **base)

    S_TITLE   = style("Title", fontName="Helvetica-Bold", fontSize=22,
                      textColor=MINT, spaceAfter=4, alignment=TA_CENTER)
    S_HEADER  = style("Header", fontName="Helvetica", fontSize=11,
                      textColor=MUTED, spaceAfter=16, alignment=TA_CENTER)
    S_H2      = style("H2", fontName="Helvetica-Bold", fontSize=13,
                      textColor=SKY, spaceBefore=20, spaceAfter=8)
    S_H3      = style("H3", fontName="Helvetica-Bold", fontSize=11,
                      textColor=MINT, spaceBefore=10, spaceAfter=4)
    S_BODY    = style("Body", leading=16, spaceAfter=10, alignment=TA_JUSTIFY)
    S_QUOTE   = style("Quote", fontName="Helvetica-Bold", fontSize=11,
                      textColor=MINT, leading=16, spaceAfter=8,
                      leftIndent=18, borderPad=8)
    S_LABEL   = style("Label", fontName="Helvetica-Bold", textColor=MINT, spaceAfter=2)
    S_FOOTER  = style("Footer", fontSize=8, textColor=MUTED,
                      alignment=TA_CENTER, spaceBefore=6)
    S_CAPTION = style("Caption", fontSize=9, textColor=MUTED, spaceAfter=6)
    S_WARN    = style("Warn", fontName="Helvetica-Bold", textColor=WARM,
                      fontSize=11, spaceAfter=8)

    story = []

    def hr(color=MINT, thick=1, after=12):
        return HRFlowable(width="100%", thickness=thick, color=color, spaceAfter=after)

    def table(data, col_widths, header=True):
        t = Table(data, colWidths=col_widths)
        style_cmds = [
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("GRID",       (0, 0), (-1, -1), 0.5, BORDER),
            ("PADDING",    (0, 0), (-1, -1), 8),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 0 if not header else 1), (-1, -1), [PANEL, PANEL2]),
            ("TEXTCOLOR",  (0, 0 if not header else 1), (-1, -1), TEXT),
        ]
        if header:
            style_cmds += [
                ("BACKGROUND", (0, 0), (-1, 0), BORDER),
                ("TEXTCOLOR",  (0, 0), (-1, 0), SKY),
                ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        t.setStyle(TableStyle(style_cmds))
        return t

    def key_val_table(data, col_widths):
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("FONTSIZE",   (0, 0), (-1, -1), 10),
            ("GRID",       (0, 0), (-1, -1), 0.5, BORDER),
            ("PADDING",    (0, 0), (-1, -1), 8),
            ("VALIGN",     (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (0, -1), PANEL),
            ("BACKGROUND", (1, 0), (1, -1), PANEL2),
            ("TEXTCOLOR",  (0, 0), (0, -1), MINT),
            ("TEXTCOLOR",  (1, 0), (1, -1), TEXT),
            ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ]))
        return t

    zone       = profile.get("zone", "—")
    subtype    = profile.get("primary_subtype", "—")
    sub_desc   = profile.get("subtype_description", "—")
    confidence = profile.get("zone_confidence", 0)
    axes       = profile.get("axis_scores", {})
    poles      = profile.get("pole_scores", {})
    geo        = profile.get("geometry", {})
    shape      = profile.get("shape_parameter", 1.0)
    shape_name = profile.get("shape_name", "—")
    stamp      = profile.get("primary_stamp", "None")
    stamp_scores = profile.get("stamp_scores", {})
    cap_type   = profile.get("capture_type", "No Capture")
    cap_primary = profile.get("capture_primary", "—")
    cap_intensity = profile.get("capture_intensity", 0)
    hom        = profile.get("hall_of_mirrors", {})

    # ── PAGE 1: Header + Plain-English Summary ────────────────────────────────
    story.append(Paragraph("Triaxial Orientation Theory", S_TITLE))
    story.append(Paragraph("Personal Orientation Profile", S_HEADER))
    if display_name:
        story.append(Paragraph(f"Prepared for: {display_name}", S_HEADER))
    story.append(Paragraph(
        f"Generated {datetime.utcnow().strftime('%B %d, %Y')} · ID: {session_id[:8].upper()}",
        S_HEADER
    ))
    story.append(hr())

    # Zone headline
    story.append(Paragraph("Your Orientation", S_H2))
    story.append(Paragraph(zone, S_QUOTE))
    story.append(Paragraph(f"<b>Subtype:</b> {subtype}", S_LABEL))
    story.append(Paragraph(sub_desc, S_BODY))
    story.append(Spacer(1, 0.1 * inch))

    # Zone written description
    zone_text = ZONE_SUMMARIES.get(zone, "")
    if zone_text:
        story.append(Paragraph(zone_text, S_BODY))

    subtype_note = SUBTYPE_NOTES.get(subtype, "")
    if subtype_note:
        story.append(Paragraph(f"<b>{subtype}:</b> {subtype_note}", S_BODY))

    story.append(hr(color=BORDER, thick=0.5, after=8))

    # Plain-English narrative
    story.append(Paragraph("Profile Interpretation", S_H2))
    story.append(Paragraph(
        "The following is a plain-English reading of this specific profile — "
        "not a generic zone description, but an interpretation of the actual numbers.",
        S_CAPTION
    ))
    story.append(Spacer(1, 0.05 * inch))

    narratives = _generate_narrative(profile)
    for para in narratives:
        if para.strip():
            story.append(Paragraph(para, S_BODY))

    # Hall of Mirrors flag on page 1 if detected
    if hom and hom.get("detected"):
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(
            f"⚠ Hall of Mirrors Pattern Detected (score {hom.get('score', 0):.3f})",
            S_WARN
        ))
        story.append(Paragraph(
            "The Hall of Mirrors is the 9th formation in TOT — not a zone within the octahedron "
            "but a collapse inward. The profile appears integrated from the outside but shows "
            "no genuine pole contact on any axis. Self-reported integration significantly "
            "exceeds empirically demonstrated integration. See page 3 for full detail.",
            S_BODY
        ))

    # ── PAGE 2: Axis + Pole data ──────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Axis Orientation Scores", S_H2))
    story.append(Paragraph(
        "Each axis runs between two poles. Negative scores lean toward the first pole; "
        "positive toward the second. Temporal Extension measures how active the temporal "
        "axis is (0 = present-only, 1 = fully extended across past and future).",
        S_CAPTION
    ))

    axis_data = [
        ["Axis", "Score", "Dominant Pole"],
        ["Vertical (Depth ↔ Surface)",
         f"{axes.get('vertical', 0):+.3f}",
         "Ohn (Depth)" if axes.get("vertical", 0) < 0 else "Hoc (Surface)"],
        ["Horizontal (Singular ↔ Collective)",
         f"{axes.get('horizontal', 0):+.3f}",
         "Him (Singular)" if axes.get("horizontal", 0) < 0 else "Allmen (Collective)"],
        ["Temporal Extension",
         f"{axes.get('temporal_extension', 0):.3f}", "—"],
        ["Temporal Balance (Past ↔ Future)",
         f"{axes.get('temporal_balance', 0):+.3f}",
         "Wasonce (Past)" if axes.get("temporal_balance", 0) < 0 else "Willbe (Future)"],
    ]
    story.append(table(axis_data, [2.8 * inch, 1.2 * inch, 2.5 * inch]))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("Axis Interpretation", S_H3))
    v = axes.get("vertical", 0)
    h = axes.get("horizontal", 0)
    t_ext = axes.get("temporal_extension", 0)

    axis_interp = []
    if abs(v) > 0.5:
        dom = "depth (Ohn)" if v < 0 else "surface (Hoc)"
        axis_interp.append(f"<b>Vertical:</b> Strongly {dom}-dominant. "
                           f"The {('depth' if v < 0 else 'surface')} register is the primary mode of engagement with experience.")
    elif abs(v) > 0.2:
        dom = "depth" if v < 0 else "surface"
        axis_interp.append(f"<b>Vertical:</b> Moderately {dom}-leaning. Both poles are accessible but {dom} is the center of gravity.")
    else:
        axis_interp.append("<b>Vertical:</b> Near-balanced. The profile can access both depth and surface registers without strong pull.")

    if abs(h) > 0.3:
        dom = "singular (Him)" if h < 0 else "collective (Allmen)"
        axis_interp.append(f"<b>Horizontal:</b> {dom.capitalize()}-dominant. "
                           f"The center of gravity is {'epistemic independence' if h < 0 else 'genuine community engagement'}.")
    else:
        axis_interp.append("<b>Horizontal:</b> Near-balanced on the horizontal axis, with capacity for both independent position and community.")

    if t_ext > 0.8:
        axis_interp.append("<b>Temporal:</b> Fully extended. Both past and future are active obligations, not background context.")
    elif t_ext > 0.5:
        axis_interp.append("<b>Temporal:</b> Moderately active. Temporal orientation is present but not at full load.")
    else:
        axis_interp.append("<b>Temporal:</b> Largely collapsed. The profile is primarily present-oriented.")

    for line in axis_interp:
        story.append(Paragraph(line, S_BODY))

    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("Pole Scores", S_H2))
    story.append(Paragraph(
        "Raw orientation score per pole. 0 = no orientation toward this pole. "
        "1 = maximum orientation. Scores above 0.70 indicate strong contact. "
        "Scores below 0.30 indicate minimal access.",
        S_CAPTION
    ))

    pole_rows = [["Pole", "Score", "Level"]]
    for pole_name, score in poles.items():
        if score >= 0.75:
            level = "Strong"
        elif score >= 0.50:
            level = "Moderate"
        elif score >= 0.30:
            level = "Low"
        else:
            level = "Minimal"
        pole_rows.append([pole_name, f"{score:.3f}", level])
    story.append(table(pole_rows, [3.0 * inch, 1.2 * inch, 2.3 * inch]))

    # ── PAGE 3: Geometry, Stamps, Capture, HoM ───────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Geometric Profile", S_H2))
    story.append(Paragraph(
        "The geometric profile describes the shape and size of the interior orientation space — "
        "how much room there is to move, how well the axes integrate, and where the boundaries are.",
        S_CAPTION
    ))

    geom_data = [
        ["Shape Parameter (p)", f"{shape:.3f}"],
        ["Shape Name", shape_name],
        ["Interior Volume", f"{profile.get('interior_volume', 0):.4f}"],
        ["Distance from Center", f"{profile.get('distance_from_center', 0):.4f}"],
        ["Distance from Boundary", f"{profile.get('distance_from_boundary', 0):.4f}"],
        ["Weakest Axis", geo.get("weakest_axis", "—")],
        ["Strongest Axis", geo.get("strongest_axis", "—")],
        ["Axis Imbalance", f"{geo.get('axis_imbalance', 0):.3f}"],
        ["Self-Reported Integration (p)", f"{geo.get('p_self_report', 1.0):.3f}"],
        ["Empirical Integration (p)", f"{geo.get('p_empirical', 1.0):.3f}"],
        ["Zone Confidence", f"{round(confidence * 100)}%"],
    ]
    if geo.get("deformations"):
        geom_data.append(["Deformations", ", ".join(geo["deformations"])])

    story.append(key_val_table(geom_data, [2.5 * inch, 4.0 * inch]))
    story.append(Spacer(1, 0.1 * inch))

    shape_text = SHAPE_DESCRIPTIONS.get(shape_name, "")
    if shape_text:
        story.append(Paragraph("<b>Shape Interpretation:</b> " + shape_text, S_BODY))

    story.append(Paragraph("Intergenerational Stamp Analysis", S_H2))
    story.append(Paragraph(
        "Stamps are inherited geometric deformations — orientation patterns transmitted "
        "across generations that shape the octahedral interior space before any "
        "personal history begins. They are detected by correlating pole scores "
        "against known inherited deformation signatures.",
        S_CAPTION
    ))
    story.append(Paragraph(f"<b>Primary Stamp:</b> {stamp}", S_LABEL))

    stamp_text = STAMP_DESCRIPTIONS.get(stamp, STAMP_DESCRIPTIONS["None"])
    story.append(Paragraph(stamp_text, S_BODY))

    if stamp_scores:
        stamp_rows = [["Stamp", "Score", "Status"]]
        for s_name, s_score in stamp_scores.items():
            status = "Detected" if s_score > 0.40 else "Below threshold"
            stamp_rows.append([s_name, f"{s_score:.3f}", status])
        story.append(table(stamp_rows, [2.8 * inch, 1.2 * inch, 2.5 * inch]))

    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Capture Analysis", S_H2))
    story.append(Paragraph(
        "A capture indicates that orientation has become fixed toward a particular "
        "pole (Vertex), pair of poles (Edge), or zone face. Captures are not inherently "
        "pathological — they describe the structural pull of the current configuration.",
        S_CAPTION
    ))

    cap_data = [
        ["Capture Type", cap_type],
        ["Primary Configuration", cap_primary],
        ["Intensity", f"{cap_intensity:.3f}"],
    ]
    story.append(key_val_table(cap_data, [2.5 * inch, 4.0 * inch]))

    # Hall of Mirrors
    story.append(Spacer(1, 0.15 * inch))
    story.append(Paragraph("9th Formation: Hall of Mirrors", S_H2))
    story.append(Paragraph(
        "The Hall of Mirrors is not a zone within the octahedron. It is a collapse inward — "
        "a self-referential epistemic trap in which the person references all orientations "
        "through an internal framework without making genuine contact with any pole. "
        "It is detected by the divergence between self-reported and empirically demonstrated "
        "integration capacity, combined with pole undifferentiation and center proximity.",
        S_CAPTION
    ))

    hom_detected = hom.get("detected", False) if hom else False
    hom_score = hom.get("score", 0) if hom else 0
    hom_components = hom.get("components", {}) if hom else {}

    hom_data = [
        ["Detection Status", "DETECTED" if hom_detected else "Not Detected"],
        ["Composite Score", f"{hom_score:.3f} (threshold: 0.580)"],
        ["Pole Undifferentiation", f"{hom_components.get('pole_undifferentiation', 0):.3f}"],
        ["Center Proximity", f"{hom_components.get('center_proximity', 0):.3f}"],
        ["Integration Divergence", f"{hom_components.get('integration_divergence', 0):.3f}"],
        ["Epistemic Subscale", f"{hom_components.get('epistemic_subscale', 0):.3f}"],
    ]
    story.append(key_val_table(hom_data, [2.5 * inch, 4.0 * inch]))

    if hom_detected:
        story.append(Spacer(1, 0.05 * inch))
        story.append(Paragraph(
            "Hall of Mirrors detected. The profile shows the characteristic divergence: "
            "self-reported integration is significantly higher than empirically demonstrated "
            "integration, combined with pole scores that cluster near mid-range rather than "
            "showing genuine directional contact. This is geometrically distinct from Zone VIII "
            "(The Somey), where multiple poles are actively elevated and integration is "
            "demonstrated rather than only self-reported.",
            S_BODY
        ))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3 * inch))
    story.append(hr(color=MUTED, thick=0.5, after=6))
    story.append(Paragraph(
        "Triaxial Orientation Theory — Ross Erickson / Avner Media · Pre-validation research instrument",
        S_FOOTER
    ))

    doc.build(story)
    return buf.getvalue()


def _fallback_pdf(profile: Dict, session_id: str) -> bytes:
    lines = [
        "TOT ORIENTATION PROFILE",
        "=" * 40,
        f"ID: {session_id[:8].upper()}",
        f"Date: {datetime.utcnow().strftime('%Y-%m-%d')}",
        "",
        f"Zone: {profile.get('zone', '—')}",
        f"Subtype: {profile.get('primary_subtype', '—')}",
        f"Shape Parameter: {profile.get('shape_parameter', 0):.3f}",
        "",
        "Axis Scores:",
    ]
    for k, v in profile.get("axis_scores", {}).items():
        lines.append(f"  {k}: {v:+.3f}" if isinstance(v, float) else f"  {k}: {v}")
    return "\n".join(lines).encode("utf-8")
