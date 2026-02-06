def calculate_investor_score(metrics, risk_score):
    """
    Advanced Investor Readiness Scoring Model
    Returns investor_score (0–100), category, breakdown
    """

    score = 0
    breakdown = {}

    # ----------------------------
    # 1. Profitability (25%)
    # ----------------------------
    if metrics["net_margin"] >= 20:
        profitability_score = 25
    elif metrics["net_margin"] >= 10:
        profitability_score = 18
    elif metrics["net_margin"] >= 5:
        profitability_score = 10
    else:
        profitability_score = 3

    score += profitability_score
    breakdown["profitability"] = profitability_score

    # ----------------------------
    # 2. Growth Proxy (15%)
    # Using return_on_assets as proxy until historical growth exists
    # ----------------------------
    if metrics["return_on_assets"] >= 15:
        growth_score = 15
    elif metrics["return_on_assets"] >= 8:
        growth_score = 10
    elif metrics["return_on_assets"] >= 5:
        growth_score = 6
    else:
        growth_score = 2

    score += growth_score
    breakdown["growth_potential"] = growth_score

    # ----------------------------
    # 3. Liquidity Stability (15%)
    # ----------------------------
    if metrics["current_ratio"] >= 2:
        liquidity_score = 15
    elif metrics["current_ratio"] >= 1.5:
        liquidity_score = 10
    elif metrics["current_ratio"] >= 1:
        liquidity_score = 6
    else:
        liquidity_score = 2

    score += liquidity_score
    breakdown["liquidity"] = liquidity_score

    # ----------------------------
    # 4. Leverage Discipline (15%)
    # ----------------------------
    if metrics["debt_to_equity"] <= 0.5:
        leverage_score = 15
    elif metrics["debt_to_equity"] <= 1:
        leverage_score = 10
    elif metrics["debt_to_equity"] <= 2:
        leverage_score = 6
    else:
        leverage_score = 2

    score += leverage_score
    breakdown["leverage"] = leverage_score

    # ----------------------------
    # 5. Operational Efficiency (10%)
    # ----------------------------
    if metrics["inventory_turnover"] >= 5:
        efficiency_score = 10
    elif metrics["inventory_turnover"] >= 3:
        efficiency_score = 7
    elif metrics["inventory_turnover"] >= 2:
        efficiency_score = 5
    else:
        efficiency_score = 2

    score += efficiency_score
    breakdown["efficiency"] = efficiency_score

    # ----------------------------
    # 6. Risk Dependency Adjustment (20%)
    # Investors care about risk health
    # ----------------------------
    if risk_score >= 750:
        risk_component = 20
    elif risk_score >= 650:
        risk_component = 15
    elif risk_score >= 550:
        risk_component = 10
    else:
        risk_component = 3

    score += risk_component
    breakdown["risk_alignment"] = risk_component

    # Final normalization
    investor_score = min(score, 100)

    # Categorization
    if investor_score >= 80:
        category = "Highly Investment Ready"
    elif investor_score >= 65:
        category = "Investment Ready"
    elif investor_score >= 50:
        category = "Growth Potential"
    else:
        category = "Not Investment Ready"

    return {
        "investor_score": investor_score,
        "category": category,
        "breakdown": breakdown
    }
