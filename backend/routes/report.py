from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Business, FinancialStatement
from services.report_generator import build_investor_report_pdf
from services.financial_engine import calculate_financial_metrics
from services.risk_engine import calculate_risk_score
from services.investor_engine import calculate_investor_score
from services.fraud_engine import detect_fraud
from services.esg_engine import calculate_esg_score
from services.warning_engine import generate_warnings
from services.ai_engine import generate_ai_summary
from services.benchmarking_engine import benchmark_against_industry, industry_risk_modifier
from services.product_recommendation_engine import recommend_products
from utils.error_handler import api_error_response


router = APIRouter()


@router.get("/report/{business_id}")
def generate_investor_report(
    business_id: int,
    lang: str = "en",
    db: Session = Depends(get_db),
):
    """
    Generate an investor-ready PDF report consolidating:
        - Metrics
        - Risk
        - ESG
        - Fraud flags
        - Forecast snapshot
        - AI recommendations
    """

    try:
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return api_error_response(
                status_code=404,
                error_code="BUSINESS_NOT_FOUND",
                message="No business found for the given business_id.",
                details=f"business_id={business_id}",
            )

        # Get latest financial statement and build analysis payload
        financial = (
            db.query(FinancialStatement)
            .filter(FinancialStatement.business_id == business_id)
            .order_by(FinancialStatement.created_at.desc())
            .first()
        )

        if not financial:
            return api_error_response(
                status_code=404,
                error_code="NO_FINANCIAL_DATA",
                message="No financial data found for report generation.",
                details=f"business_id={business_id}",
            )

        # Build analysis payload (simplified, without DB writes)
        metrics = calculate_financial_metrics(financial)
        industry = business.industry or "Unknown"

        risk_result = calculate_risk_score(metrics)
        benchmarking = benchmark_against_industry(metrics, industry=industry)
        modifier = industry_risk_modifier(benchmarking)
        base_risk_score = risk_result["risk_score"]
        adjusted_risk_score = max(300, min(900, base_risk_score + modifier))
        risk_score_value = adjusted_risk_score

        investor_result = calculate_investor_score(metrics, risk_score_value)
        fraud_flags = detect_fraud(financial)
        esg_result = calculate_esg_score(financial)
        warnings_result = generate_warnings(metrics)
        ai_recommendations = generate_ai_summary(
            metrics=metrics,
            risk_data=risk_result,
            investor_data=investor_result,
            esg_data=esg_result,
            warnings=warnings_result,
            fraud_flags=fraud_flags,
            language=lang,
        )

        analysis_result = {
            "metrics": metrics,
            "industry": industry,
            "risk": {"score": risk_score_value, "category": risk_result.get("category", "Unknown")},
            "investor": {"score": investor_result["investor_score"], "category": investor_result["category"]},
            "fraud_flags": fraud_flags,
            "esg": {"score": esg_result["esg_score"], "category": esg_result["category"]},
            "warnings": warnings_result.get("warnings", []),
            "ai_recommendations": ai_recommendations,
        }

        # Forecast data (optional, simplified)
        forecast_data = None

        try:
            pdf_bytes = build_investor_report_pdf(
                business_name=business.name,
                analysis_payload=analysis_result,
                forecast_payload=forecast_data,
            )
        except Exception as exc:
            return api_error_response(
                status_code=500,
                error_code="REPORT_GENERATION_FAILED",
                message="Failed to generate PDF report.",
                details=str(exc),
            )

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="fhat_report_{business_id}.pdf"'
            },
        )

    except Exception as exc:  # pragma: no cover - defensive
        return api_error_response(
            status_code=500,
            error_code="REPORT_INTERNAL_ERROR",
            message="Unexpected error while generating investor report.",
            details=str(exc),
        )

