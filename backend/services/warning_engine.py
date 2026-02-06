def generate_warnings(metrics, forecast_summary=None, risk_trend=None):
    """
    Early Warning Intelligence Engine.

    Detects financial stress signals and, in Phase 3, adds a predictive
    deterioration probability based on optional forecast and risk-trend inputs.

    Args:
        metrics: Current-period metrics from `calculate_financial_metrics`.
        forecast_summary: Optional dict produced by the forecasting engine,
            used to infer forward-looking liquidity / cash trends.
        risk_trend: Optional list of historical risk scores (oldest -> newest).
    """

    warnings = []

    # ----------------------------
    # 1. Liquidity Stress
    # ----------------------------
    if metrics["current_ratio"] < 1:
        warnings.append({
            "type": "Liquidity Risk",
            "severity": "High",
            "message": "Current ratio below 1. Immediate liquidity pressure detected."
        })

    elif metrics["current_ratio"] < 1.3:
        warnings.append({
            "type": "Liquidity Watch",
            "severity": "Medium",
            "message": "Liquidity buffer is thinning. Monitor working capital closely."
        })

    # ----------------------------
    # 2. Debt Stress
    # ----------------------------
    if metrics["debt_to_equity"] > 2:
        warnings.append({
            "type": "Debt Overexposure",
            "severity": "High",
            "message": "Debt-to-equity ratio critically high. Risk of financial strain."
        })

    # ----------------------------
    # 3. Profitability Decline
    # ----------------------------
    if metrics["net_margin"] < 5:
        warnings.append({
            "type": "Low Profitability",
            "severity": "High",
            "message": "Net margin critically low. Sustainability risk increasing."
        })

    # ----------------------------
    # 4. Receivables Pressure
    # ----------------------------
    if metrics["receivable_days"] > 90:
        warnings.append({
            "type": "Receivables Delay",
            "severity": "Medium",
            "message": "Receivables collection cycle is extended beyond 90 days."
        })

    # ----------------------------
    # 5. Inventory Inefficiency
    # ----------------------------
    if metrics["inventory_turnover"] < 2:
        warnings.append({
            "type": "Inventory Stagnation",
            "severity": "Medium",
            "message": "Inventory turnover is slow. Capital may be locked in stock."
        })

    # ----------------------------
    # 6. Survival Risk Indicator
    # ----------------------------
    survival_score = 100

    if metrics["working_capital"] < 0:
        survival_score -= 40

    if metrics["current_ratio"] < 1:
        survival_score -= 30

    if metrics["net_margin"] < 5:
        survival_score -= 20

    if metrics["debt_to_equity"] > 2:
        survival_score -= 20

    survival_score = max(survival_score, 0)

    if survival_score < 40:
        warnings.append({
            "type": "Business Survival Risk",
            "severity": "Critical",
            "message": "High probability of financial distress within short-term horizon."
        })

    # ----------------------------
    # 7. Predictive Deterioration Probability
    # ----------------------------
    deterioration_probability = 0.0

    # Risk-trend contribution
    if risk_trend and len(risk_trend) >= 2:
        delta = risk_trend[-1] - risk_trend[0]
        if delta < 0:
            # Worsening (score falling)
            deterioration_probability += min(40.0, abs(delta) / 10.0)

    # Forecast contribution (cash-flow projections) - enhanced with new signals
    if forecast_summary:
        from services.forecasting_engine import extract_forecast_signals
        
        try:
            forecast_signals = extract_forecast_signals(forecast_summary)
            
            # Use enhanced signals
            if forecast_signals.get("liquidity_risk_forecast"):
                deterioration_probability += 30.0
                warnings.append({
                    "type": "Forecasted Liquidity Risk",
                    "severity": "High",
                    "message": f"Forecast indicates {forecast_signals.get('negative_cashflow_months', 0)} months of negative cashflow ahead."
                })
            
            runway = forecast_signals.get("cash_runway_months", float("inf"))
            if runway < 3:
                deterioration_probability += 25.0
                warnings.append({
                    "type": "Cash Runway Critical",
                    "severity": "Critical",
                    "message": f"Projected cash runway is only {runway:.1f} months. Immediate action required."
                })
            elif runway < 6:
                deterioration_probability += 15.0
                warnings.append({
                    "type": "Cash Runway Warning",
                    "severity": "Medium",
                    "message": f"Projected cash runway is {runway:.1f} months. Monitor closely."
                })
            
            trend = forecast_signals.get("trend_direction", "unknown")
            if trend == "deteriorating":
                deterioration_probability += 20.0
            
        except Exception:
            # Fallback to simple logic if extraction fails
            cash_proj = forecast_summary.get("cashflow_projection", {})
            future = cash_proj.get("future", [])
            if future:
                negative_months = sum(1 for m in future if m.get("value", 0) < 0)
                deterioration_probability += negative_months * 10.0

    # Clamp to [0, 100]
    deterioration_probability = max(0.0, min(100.0, deterioration_probability))

    if deterioration_probability >= 50.0:
        warnings.append({
            "type": "Predictive Deterioration",
            "severity": "High",
            "message": "Forward-looking signals indicate elevated probability of financial deterioration."
        })
    elif deterioration_probability >= 25.0:
        warnings.append({
            "type": "Deterioration Watch",
            "severity": "Medium",
            "message": "Forecast and risk trend suggest emerging downside risk. Monitor closely."
        })

    return {
        "warnings": warnings,
        "survival_score": survival_score,
        "deterioration_probability": round(deterioration_probability, 1)
    }
