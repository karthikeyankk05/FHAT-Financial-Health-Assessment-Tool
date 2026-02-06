def calculate_financial_metrics(financial):
    """
    Core Financial Intelligence Engine.

    Accepts a FinancialStatement ORM instance and returns a structured metrics
    dictionary used by downstream engines (risk, investor, ESG, forecasting).

    Phase 2 enhancements:
        - Track loan balance
        - Debt servicing ratio
        - Interest burden ratio
        - Negative revenue flag (for anomaly handling)
    """

    revenue = financial.revenue or 0
    expenses = financial.expenses or 0
    assets = financial.assets or 0
    liabilities = financial.liabilities or 0
    receivables = financial.receivables or 0
    payables = financial.payables or 0
    inventory = financial.inventory or 0
    debt = financial.debt or 0

    negative_revenue = revenue < 0
    safe_revenue = revenue if revenue > 0 else 0

    # ----------------------------
    # Profitability Metrics
    # ----------------------------

    gross_margin = ((safe_revenue - expenses) / safe_revenue * 100) if safe_revenue > 0 else 0
    net_margin = (safe_revenue - expenses) / safe_revenue * 100 if safe_revenue > 0 else 0
    operating_ratio = (expenses / safe_revenue * 100) if safe_revenue > 0 else 0

    # ----------------------------
    # Liquidity Metrics
    # ----------------------------

    current_ratio = (assets / liabilities) if liabilities > 0 else 0
    quick_ratio = ((assets - inventory) / liabilities) if liabilities > 0 else 0
    working_capital = assets - liabilities

    # ----------------------------
    # Leverage & Debt Metrics
    # ----------------------------

    equity = assets - liabilities
    debt_to_equity = (debt / equity) if equity > 0 else 0

    # Treat `debt` as total loan balance for Phase 2.
    loan_balance = debt

    # Debt servicing ratio: approximate as debt / safe_revenue.
    debt_servicing_ratio = (debt / safe_revenue) if safe_revenue > 0 else 0

    # Interest burden ratio: simplified heuristic using a proxy 8% interest rate.
    assumed_interest = debt * 0.08
    interest_burden_ratio = (assumed_interest / safe_revenue) if safe_revenue > 0 else 0

    # ----------------------------
    # Efficiency Metrics
    # ----------------------------

    receivable_days = (receivables / safe_revenue * 365) if safe_revenue > 0 else 0
    payable_days = (payables / expenses * 365) if expenses > 0 else 0
    inventory_turnover = (safe_revenue / inventory) if inventory > 0 else 0

    # ----------------------------
    # Return Metrics
    # ----------------------------

    return_on_assets = ((safe_revenue - expenses) / assets * 100) if assets > 0 else 0

    return {
        "gross_margin": round(gross_margin, 2),
        "net_margin": round(net_margin, 2),
        "operating_ratio": round(operating_ratio, 2),
        "current_ratio": round(current_ratio, 2),
        "quick_ratio": round(quick_ratio, 2),
        "working_capital": round(working_capital, 2),
        "debt_to_equity": round(debt_to_equity, 2),
        "receivable_days": round(receivable_days, 2),
        "payable_days": round(payable_days, 2),
        "inventory_turnover": round(inventory_turnover, 2),
        "return_on_assets": round(return_on_assets, 2),
        # Phase 2 additions
        "loan_balance": round(loan_balance, 2),
        "debt_servicing_ratio": round(debt_servicing_ratio, 4),
        "interest_burden_ratio": round(interest_burden_ratio, 4),
        "negative_revenue_flag": bool(negative_revenue),
    }
