def detect_fraud(financial):
    """
    Advanced Fraud & Financial Anomaly Detection Engine.

    Phase 3 upgrades:
        - Adds anomaly scoring
        - Multi-factor rule logic
        - Simple pattern detection on cash / revenue spikes

    Returns:
        List[Dict] of fraud flags. Each flag may include an `anomaly_score`
        component that can be aggregated by downstream consumers.
    """

    flags = []
    anomaly_score = 0

    revenue = financial.revenue or 0
    expenses = financial.expenses or 0
    receivables = financial.receivables or 0
    payables = financial.payables or 0
    inventory = financial.inventory or 0
    assets = financial.assets or 0
    liabilities = financial.liabilities or 0
    debt = financial.debt or 0

    # ----------------------------
    # 1. Expense Anomaly
    # ----------------------------
    if revenue > 0 and expenses / revenue > 0.95:
        anomaly_score += 20
        flags.append({
            "type": "Expense Anomaly",
            "severity": "High",
            "message": "Expenses exceed 95% of revenue. Possible cost manipulation or unsustainable operations.",
            "anomaly_score": 20
        })

    # ----------------------------
    # 2. Receivables Risk
    # ----------------------------
    if revenue > 0 and receivables / revenue > 0.6:
        anomaly_score += 15
        flags.append({
            "type": "Receivables Concentration",
            "severity": "Medium",
            "message": "Receivables exceed 60% of revenue. Risk of revenue inflation or delayed collections.",
            "anomaly_score": 15
        })

    # ----------------------------
    # 3. Payables Suppression
    # ----------------------------
    if expenses > 0 and payables / expenses < 0.05:
        anomaly_score += 10
        flags.append({
            "type": "Payables Irregularity",
            "severity": "Medium",
            "message": "Very low payables relative to expenses. Possible off-book liabilities.",
            "anomaly_score": 10
        })

    # ----------------------------
    # 4. Inventory Inflation Risk
    # ----------------------------
    if assets > 0 and inventory / assets > 0.7:
        anomaly_score += 10
        flags.append({
            "type": "Inventory Inflation",
            "severity": "Medium",
            "message": "Inventory forms more than 70% of assets. Risk of stock overvaluation.",
            "anomaly_score": 10
        })

    # ----------------------------
    # 5. Debt Misalignment
    # ----------------------------
    equity = assets - liabilities
    if equity > 0 and debt / equity > 3:
        anomaly_score += 15
        flags.append({
            "type": "Debt Structuring Risk",
            "severity": "High",
            "message": "Debt exceeds 3x equity. Possible over-leveraging or aggressive borrowing.",
            "anomaly_score": 15
        })

    # ----------------------------
    # 6. Round-Number Suspicion (Simple Proxy)
    # ----------------------------
    if revenue % 100000 == 0 and expenses % 100000 == 0 and revenue > 0:
        anomaly_score += 5
        flags.append({
            "type": "Rounded Financial Reporting",
            "severity": "Low",
            "message": "Financial figures appear heavily rounded. Recommend validation.",
            "anomaly_score": 5
        })

    # ----------------------------
    # 7. Asset-Liability Imbalance
    # ----------------------------
    if liabilities > assets:
        anomaly_score += 20
        flags.append({
            "type": "Negative Net Worth",
            "severity": "Critical",
            "message": "Liabilities exceed assets. High financial distress risk.",
            "anomaly_score": 20
        })

    # ----------------------------
    # 8. Cash / Revenue Spike Pattern (simple proxy)
    # ----------------------------
    if revenue > 0 and assets > 0 and revenue / assets > 3 and receivables / revenue < 0.1:
        anomaly_score += 10
        flags.append({
            "type": "Cashflow Spike Pattern",
            "severity": "Medium",
            "message": "Very high revenue relative to assets with low receivables; review for unusual cash spikes.",
            "anomaly_score": 10
        })

    if anomaly_score > 0:
        flags.append({
            "type": "Fraud Anomaly Score",
            "severity": "Info",
            "message": f"Aggregate anomaly score: {anomaly_score}",
            "anomaly_score": anomaly_score
        })

    return flags
