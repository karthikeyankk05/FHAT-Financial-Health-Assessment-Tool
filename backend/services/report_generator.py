"""
Investor-ready PDF report generator.

Generates a single consolidated PDF containing:
    - Core metrics
    - Risk
    - ESG
    - Fraud flags
    - Forecast summary
    - AI recommendations

Uses ReportLab for PDF generation. This is intentionally layout-simple but
structured enough for enterprise reporting pipelines.
"""

from __future__ import annotations

from io import BytesIO
from typing import Dict, Any

try:
    from reportlab.lib.pagesizes import A4  # type: ignore[import]
    from reportlab.lib.styles import getSampleStyleSheet  # type: ignore[import]
    from reportlab.platypus import (  # type: ignore[import]
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )
    from reportlab.lib import colors  # type: ignore[import]
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def _section_title(text: str, styles):
    return Paragraph(f"<b>{text}</b>", styles["Heading3"])


def _key_value_table(data: Dict[str, Any], styles):
    rows = [["Metric", "Value"]]
    for k, v in data.items():
        rows.append([str(k), str(v)])
    table = Table(rows, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )
    return table


def build_investor_report_pdf(
    business_name: str,
    analysis_payload: Dict[str, Any],
    forecast_payload: Dict[str, Any] | None = None,
) -> bytes:
    """
    Build a single-page (or few-page) investor-ready PDF report.

    Args:
        business_name: Human-readable business name to show on report.
        analysis_payload: Response payload from `/analyze/{business_id}`.
        forecast_payload: Optional payload from `/forecast/{business_id}`.

    Returns:
        PDF bytes suitable for streaming as a download.

    Raises:
        ImportError: If reportlab is not installed.
    """

    if not REPORTLAB_AVAILABLE:
        raise ImportError(
            "reportlab is not installed. Install it with: pip install reportlab"
        )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    story = []

    # Header
    story.append(Paragraph(f"<b>FHAT Investor Report - {business_name}</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # Metrics
    metrics = analysis_payload.get("metrics", {})
    story.append(_section_title("Financial Metrics", styles))
    if metrics:
        story.append(_key_value_table(metrics, styles))
    else:
        story.append(Paragraph("No metrics available.", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Risk
    risk = analysis_payload.get("risk", {})
    story.append(_section_title("Risk Profile", styles))
    if risk:
        risk_table_data = {
            "Risk Score": risk.get("score"),
            "Category": risk.get("category"),
        }
        story.append(_key_value_table(risk_table_data, styles))
    else:
        story.append(Paragraph("No risk assessment available.", styles["Normal"]))
    story.append(Spacer(1, 12))

    # ESG
    esg = analysis_payload.get("esg", {})
    story.append(_section_title("ESG Summary", styles))
    if esg:
        esg_table_data = {
            "ESG Score": esg.get("score"),
            "Category": esg.get("category"),
        }
        story.append(_key_value_table(esg_table_data, styles))
    else:
        story.append(Paragraph("No ESG data available.", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Fraud flags
    fraud_flags = analysis_payload.get("fraud_flags", [])
    story.append(_section_title("Fraud & Anomaly Flags", styles))
    if fraud_flags:
        for flag in fraud_flags:
            story.append(
                Paragraph(
                    f"- [{flag.get('severity', 'Info')}] {flag.get('type', '')}: {flag.get('message', '')}",
                    styles["Normal"],
                )
            )
    else:
        story.append(Paragraph("No fraud anomalies detected.", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Forecast
    story.append(_section_title("Forecast Snapshot", styles))
    if forecast_payload:
        cf = forecast_payload.get("forecast", {}).get("cashflow_projection", {})
        horizon = forecast_payload.get("forecast_horizon_months")
        if cf:
            future = cf.get("future", [])
            if future:
                first_period = future[0]["period"]
                last_period = future[-1]["period"]
                story.append(
                    Paragraph(
                        f"Cashflow forecast available for {len(future)} periods "
                        f"({first_period} to {last_period}).",
                        styles["Normal"],
                    )
                )
            else:
                story.append(Paragraph("Cashflow forecast has no future periods.", styles["Normal"]))
        else:
            story.append(Paragraph("No cashflow forecast available.", styles["Normal"]))

        if horizon:
            story.append(
                Paragraph(f"Forecast horizon: {horizon} months.", styles["Normal"])
            )
    else:
        story.append(Paragraph("Forecast section not generated for this report.", styles["Normal"]))
    story.append(Spacer(1, 12))

    # AI recommendations
    story.append(_section_title("AI CFO Recommendations", styles))
    recos = analysis_payload.get("ai_recommendations", {})
    if recos:
        for key, title in [
            ("strategic_actions", "Strategic Actions"),
            ("cost_optimization", "Cost Optimisation"),
            ("liquidity_improvements", "Liquidity Improvements"),
            ("funding_recommendations", "Funding Recommendations"),
        ]:
            items = recos.get(key, [])
            if not items:
                continue
            story.append(Paragraph(f"<b>{title}</b>", styles["Normal"]))
            for item in items:
                story.append(Paragraph(f"- {item}", styles["Normal"]))
    else:
        story.append(Paragraph("No AI recommendations available.", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

