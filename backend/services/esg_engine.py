def calculate_esg_score(financial):
    """
    ESG Scoring Engine
    Returns ESG score (0–100), category, breakdown
    """

    revenue = financial.revenue or 0
    expenses = financial.expenses or 0
    receivables = financial.receivables or 0
    payables = financial.payables or 0
    assets = financial.assets or 0
    liabilities = financial.liabilities or 0
    debt = financial.debt or 0

    breakdown = {}
    total_score = 0

    # ----------------------------
    # E — Environmental (40%)
    # Proxy via cost efficiency + asset balance
    # ----------------------------

    environmental_score = 0

    if revenue > 0:
        cost_ratio = expenses / revenue

        if cost_ratio < 0.6:
            environmental_score += 20
        elif cost_ratio < 0.75:
            environmental_score += 12
        else:
            environmental_score += 5

    if assets > 0 and liabilities / assets < 0.5:
        environmental_score += 20
    else:
        environmental_score += 10

    breakdown["environmental"] = environmental_score
    total_score += environmental_score

    # ----------------------------
    # S — Social (30%)
    # Proxy via receivables & payables behavior
    # ----------------------------

    social_score = 0

    if revenue > 0 and receivables / revenue < 0.4:
        social_score += 15
    else:
        social_score += 7

    if expenses > 0 and payables / expenses > 0.2:
        social_score += 15
    else:
        social_score += 7

    breakdown["social"] = social_score
    total_score += social_score

    # ----------------------------
    # G — Governance (30%)
    # Proxy via leverage discipline + balance sheet health
    # ----------------------------

    governance_score = 0

    equity = assets - liabilities

    if equity > 0 and debt / equity < 1:
        governance_score += 15
    else:
        governance_score += 7

    if liabilities <= assets:
        governance_score += 15
    else:
        governance_score += 5

    breakdown["governance"] = governance_score
    total_score += governance_score

    # Final ESG Score
    esg_score = min(total_score, 100)

    # Categorization
    if esg_score >= 80:
        category = "Sustainable Leader"
    elif esg_score >= 65:
        category = "Responsible"
    elif esg_score >= 50:
        category = "Moderate"
    else:
        category = "Needs Improvement"

    return {
        "esg_score": esg_score,
        "category": category,
        "breakdown": breakdown
    }
