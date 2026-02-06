"""
Bank / NBFC financial product recommendation engine.

Maps risk score and basic metrics into indicative product-fit suggestions:
    - Loan eligibility
    - Working capital loan
    - Overdraft
    - Term loan
"""

from __future__ import annotations

from typing import Dict, List, Optional


def recommend_products(
    risk_score: int,
    metrics: Dict,
    forecast_data: Optional[Dict] = None,
) -> Dict:
    """
    Build a structured recommendation payload from risk + metrics + forecast.

    Args:
        risk_score: FHAT risk score (300–900).
        metrics: Financial metrics dict from `calculate_financial_metrics`.
        forecast_data: Optional forecast result dict for forward-looking insights.
    """

    recommendations: List[Dict] = []

    # Base eligibility tiers
    if risk_score >= 800:
        base_eligibility = "Prime"
    elif risk_score >= 700:
        base_eligibility = "Standard"
    elif risk_score >= 600:
        base_eligibility = "Borderline"
    else:
        base_eligibility = "High Risk"

    # Working capital suitability
    working_capital = metrics.get("working_capital", 0)
    current_ratio = metrics.get("current_ratio", 0)
    debt_to_equity = metrics.get("debt_to_equity", 0)

    # Forecast-enhanced product recommendations
    forecast_insights = {}
    if forecast_data:
        from services.forecasting_engine import get_forecast_for_product_recommendation
        try:
            forecast_insights = get_forecast_for_product_recommendation(forecast_data)
        except Exception:
            pass
    
    funding_need = forecast_insights.get("funding_need_indicator", "neutral")
    liquidity_forecast_score = forecast_insights.get("liquidity_forecast_score", 50)
    
    # Working capital loan (enhanced with forecast)
    if working_capital > 0 and current_ratio >= 1.2 and risk_score >= 650:
        rationale = "Positive working capital and adequate liquidity buffer."
        if funding_need == "high":
            rationale += " Forecast indicates high funding need - consider larger facility."
        recommendations.append(
            {
                "product": "Working Capital Loan",
                "fit": "Good",
                "rationale": rationale,
                "forecast_enhanced": True,
            }
        )
    elif risk_score >= 600:
        rationale = "Moderate risk profile; structure with tighter covenants."
        if liquidity_forecast_score < 40:
            rationale += " Forecast shows liquidity pressure - prioritize quick disbursement."
        recommendations.append(
            {
                "product": "Working Capital Loan",
                "fit": "Cautious",
                "rationale": rationale,
                "forecast_enhanced": True,
            }
        )

    # Overdraft facility
    if current_ratio >= 1 and working_capital >= 0:
        recommendations.append(
            {
                "product": "Overdraft Facility",
                "fit": "Good",
                "rationale": "Short-term liquidity needs can be supported by an OD line.",
            }
        )
    else:
        recommendations.append(
            {
                "product": "Overdraft Facility",
                "fit": "Weak",
                "rationale": "Thin liquidity and negative working capital; OD may increase stress.",
            }
        )

    # Term loan
    if debt_to_equity <= 1.5 and risk_score >= 700:
        recommendations.append(
            {
                "product": "Term Loan",
                "fit": "Good",
                "rationale": "Balanced leverage and healthy risk score support term funding.",
            }
        )
    elif debt_to_equity <= 2 and risk_score >= 650:
        recommendations.append(
            {
                "product": "Term Loan",
                "fit": "Cautious",
                "rationale": "Leverage acceptable but monitor DSCR and cash flows closely.",
            }
        )
    else:
        recommendations.append(
            {
                "product": "Term Loan",
                "fit": "Weak",
                "rationale": "High leverage or weak risk score; prioritize deleveraging.",
            }
        )

    result = {
        "risk_band": base_eligibility,
        "suggested_products": recommendations,
    }
    
    # Add forecast insights if available
    if forecast_insights:
        result["forecast_insights"] = forecast_insights
    
    return result

