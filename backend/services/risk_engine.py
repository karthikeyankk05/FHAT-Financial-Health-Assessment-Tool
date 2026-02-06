def calculate_risk_score(metrics):
    """
    Advanced Weighted Risk Scoring Model
    Returns risk_score (300–900) and factor breakdown
    """

    score = 900
    deductions = {}

    # ----------------------------
    # 1. Liquidity Risk (Weight: 25%)
    # ----------------------------
    if metrics["current_ratio"] < 1:
        penalty = 120
        score -= penalty
        deductions["liquidity_risk"] = penalty
    elif metrics["current_ratio"] < 1.5:
        penalty = 60
        score -= penalty
        deductions["liquidity_risk"] = penalty

    # ----------------------------
    # 2. Leverage Risk (Weight: 25%)
    # ----------------------------
    if metrics["debt_to_equity"] > 2:
        penalty = 150
        score -= penalty
        deductions["leverage_risk"] = penalty
    elif metrics["debt_to_equity"] > 1:
        penalty = 80
        score -= penalty
        deductions["leverage_risk"] = penalty

    # ----------------------------
    # 3. Profitability Risk (Weight: 20%)
    # ----------------------------
    if metrics["net_margin"] < 5:
        penalty = 100
        score -= penalty
        deductions["profitability_risk"] = penalty
    elif metrics["net_margin"] < 10:
        penalty = 50
        score -= penalty
        deductions["profitability_risk"] = penalty

    # ----------------------------
    # 4. Efficiency Risk (Weight: 15%)
    # ----------------------------
    if metrics["receivable_days"] > 90:
        penalty = 70
        score -= penalty
        deductions["receivable_delay_risk"] = penalty

    if metrics["inventory_turnover"] < 2:
        penalty = 50
        score -= penalty
        deductions["inventory_efficiency_risk"] = penalty

    # ----------------------------
    # 5. Asset Utilization (Weight: 15%)
    # ----------------------------
    if metrics["return_on_assets"] < 5:
        penalty = 60
        score -= penalty
        deductions["asset_efficiency_risk"] = penalty

    # Ensure minimum score
    risk_score = max(score, 300)

    # Categorize
    if risk_score >= 750:
        category = "Low Risk"
    elif risk_score >= 600:
        category = "Medium Risk"
    else:
        category = "High Risk"

    return {
        "risk_score": risk_score,
        "category": category,
        "deductions": deductions
    }
