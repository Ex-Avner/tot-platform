"""
TOT Report Generator — PDF output via reportlab.
"""

import io
from datetime import datetime
from typing import Dict


def generate_pdf_report(profile: Dict, session_id: str) -> bytes:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        return _fallback_pdf(profile, session_id)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter,
                            topMargin=0.75*inch, bottomMargin=0.75*inch,
                            leftMargin=inch, rightMargin=inch)

    # Colors
    DARK = colors.HexColor("#0b1021")
    MINT = colors.HexColor("#5eead4")
    SKY = colors.HexColor("#38bdf8")
    MUTED = colors.HexColor("#9fb0c5")
    WHITE = colors.white

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=22,
                                  textColor=MINT, spaceAfter=4, alignment=TA_CENTER)
    sub_style = ParagraphStyle("Sub", fontName="Helvetica", fontSize=11,
                                textColor=MUTED, spaceAfter=16, alignment=TA_CENTER)
    h2_style = ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=13,
                               textColor=SKY, spaceBefore=18, spaceAfter=6)
    body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=10,
                                 textColor=colors.HexColor("#e8ecf5"), spaceAfter=6, leading=14)
    label_style = ParagraphStyle("Label", fontName="Helvetica-Bold", fontSize=10,
                                  textColor=MINT, spaceAfter=2)

    story = []

    # Header
    story.append(Paragraph("Triaxial Orientation Theory", title_style))
    story.append(Paragraph("Personal Orientation Profile", sub_style))
    story.append(Paragraph(f"Generated {datetime.utcnow().strftime('%B %d, %Y')} · ID: {session_id[:8].upper()}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=MINT, spaceAfter=12))

    # Zone & Subtype
    story.append(Paragraph("Zone Classification", h2_style))
    zone_data = [
        ["Zone", profile.get("zone", "—")],
        ["Subtype", profile.get("primary_subtype", "—")],
        ["Subtype Description", profile.get("subtype_description", "—")],
        ["Zone Confidence", f"{round(profile.get('zone_confidence', 0) * 100)}%"],
    ]
    t = Table(zone_data, colWidths=[1.8*inch, 4.7*inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#10182e")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#0f1c33")),
        ("TEXTCOLOR", (0, 0), (0, -1), MINT),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#e8ecf5")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#10182e"), colors.HexColor("#0f1c33")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1e2a42")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("WORDWRAP", (1, 2), (1, 2), True),
    ]))
    story.append(t)

    # Axis Scores
    story.append(Paragraph("Axis Orientation Scores", h2_style))
    axes = profile.get("axis_scores", {})
    geo = profile.get("geometry", {})
    axis_data = [
        ["Axis", "Score", "Dominant Pole"],
        ["Vertical (Depth)", f"{axes.get('vertical', 0):+.3f}",
         "Ohn (Depth)" if axes.get("vertical", 0) < 0 else "Hoc (Surface)"],
        ["Horizontal (Breath)", f"{axes.get('horizontal', 0):+.3f}",
         "Him (Singular)" if axes.get("horizontal", 0) < 0 else "Allmen (Collective)"],
        ["Temporal Extension", f"{axes.get('temporal_extension', 0):.3f}", "—"],
        ["Temporal Balance", f"{axes.get('temporal_balance', 0):+.3f}",
         "Wasonce (Past)" if axes.get("temporal_balance", 0) < 0 else "Willbe (Future)"],
    ]
    t2 = Table(axis_data, colWidths=[2.2*inch, 1.2*inch, 3.1*inch])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e2a42")),
        ("TEXTCOLOR", (0, 0), (-1, 0), SKY),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#10182e"), colors.HexColor("#0f1c33")]),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#e8ecf5")),
        ("TEXTCOLOR", (1, 1), (1, -1), MINT),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1e2a42")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 0), (1, -1), "CENTER"),
    ]))
    story.append(t2)

    # Pole Scores
    story.append(Paragraph("Pole Scores", h2_style))
    poles = profile.get("pole_scores", {})
    pole_rows = [["Pole", "Score (0–1)"]]
    for pole_name, score in poles.items():
        pole_rows.append([pole_name, f"{score:.3f}"])
    t3 = Table(pole_rows, colWidths=[3.5*inch, 3*inch])
    t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e2a42")),
        ("TEXTCOLOR", (0, 0), (-1, 0), SKY),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#10182e"), colors.HexColor("#0f1c33")]),
        ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#e8ecf5")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1e2a42")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("ALIGN", (1, 1), (1, -1), "CENTER"),
    ]))
    story.append(t3)

    # Shape & Geometry
    story.append(Paragraph("Geometric Profile", h2_style))
    geom_data = [
        ["Shape Parameter (p)", f"{profile.get('shape_parameter', 1.0):.3f}"],
        ["Shape Name", profile.get("shape_name", "—")],
        ["Interior Volume", f"{profile.get('interior_volume', 0):.4f}"],
        ["Distance from Center", f"{profile.get('distance_from_center', 0):.4f}"],
        ["Distance from Boundary", f"{profile.get('distance_from_boundary', 0):.4f}"],
        ["Weakest Axis", geo.get("weakest_axis", "—")],
        ["Strongest Axis", geo.get("strongest_axis", "—")],
        ["Axis Imbalance", f"{geo.get('axis_imbalance', 0):.3f}"],
    ]
    t4 = Table(geom_data, colWidths=[2.5*inch, 4*inch])
    t4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#10182e")),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#0f1c33")),
        ("TEXTCOLOR", (0, 0), (0, -1), MINT),
        ("TEXTCOLOR", (1, 0), (1, -1), colors.HexColor("#e8ecf5")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1e2a42")),
        ("PADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(t4)

    # Capture
    story.append(Paragraph("Capture Analysis", h2_style))
    story.append(Paragraph(
        f"<b>Type:</b> {profile.get('capture_type', '—')}<br/>"
        f"<b>Primary:</b> {profile.get('capture_primary', '—')}<br/>"
        f"<b>Intensity:</b> {profile.get('capture_intensity', 0):.3f}",
        body_style
    ))

    # Stamps
    story.append(Paragraph("Intergenerational Stamp Analysis", h2_style))
    primary_stamp = profile.get("primary_stamp", "None")
    stamp_scores = profile.get("stamp_scores", {})
    story.append(Paragraph(f"<b>Primary Stamp:</b> {primary_stamp}", body_style))
    if stamp_scores:
        stamp_rows = [["Stamp", "Score"]]
        for stamp, score in stamp_scores.items():
            stamp_rows.append([stamp, f"{score:.3f}"])
        t5 = Table(stamp_rows, colWidths=[3.5*inch, 3*inch])
        t5.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e2a42")),
            ("TEXTCOLOR", (0, 0), (-1, 0), SKY),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#10182e"), colors.HexColor("#0f1c33")]),
            ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#e8ecf5")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#1e2a42")),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("ALIGN", (1, 1), (1, -1), "CENTER"),
        ]))
        story.append(t5)

    # Footer
    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MUTED))
    story.append(Paragraph(
        "Triaxial Orientation Theory — Ross Erickson / Avner Media · Pre-validation research instrument",
        ParagraphStyle("Footer", fontName="Helvetica", fontSize=8,
                       textColor=MUTED, alignment=TA_CENTER, spaceBefore=6)
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
        lines.append(f"  {k}: {v:+.3f}")
    text = "\n".join(lines)
    return text.encode("utf-8")
