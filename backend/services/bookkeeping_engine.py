"""
Rule-based bookkeeping assistance engine.

Given a list of transactional records, this module:
    - Categorizes transactions using simple keyword-based rules.
    - Detects unclassified entries.
    - Flags basic anomalies (very large amounts, unusual sign patterns).
"""

from __future__ import annotations

from typing import Dict, List, Tuple


CATEGORY_RULES: List[Tuple[str, str]] = [
    ("rent", "Rent"),
    ("salary", "Payroll"),
    ("payroll", "Payroll"),
    ("wage", "Payroll"),
    ("gst", "Taxes"),
    ("tax", "Taxes"),
    ("subscription", "Software Subscriptions"),
    ("saas", "Software Subscriptions"),
    ("hosting", "Cloud Hosting"),
    ("aws", "Cloud Hosting"),
    ("azure", "Cloud Hosting"),
    ("gcp", "Cloud Hosting"),
    ("invoice", "Customer Receipts"),
    ("payment", "Customer Receipts"),
    ("refund", "Refunds"),
]


def categorize_transaction(tx: Dict) -> Dict:
    """
    Categorize a single transaction based on its description and amount.

    The input transaction is expected to contain:
        - description: str
        - amount: float (positive = inflow, negative = outflow)

    Returns:
        Enriched transaction dict with:
            - category
            - is_unclassified
            - anomaly_flags (list[str])
    """

    description = str(tx.get("description", "")).lower()
    amount = float(tx.get("amount", 0.0))

    category = None
    for keyword, cat in CATEGORY_RULES:
        if keyword in description:
            category = cat
            break

    is_unclassified = category is None
    if is_unclassified:
        category = "Unclassified"

    anomaly_flags: List[str] = []

    # Simple anomaly heuristics
    if abs(amount) > 1_000_000:
        anomaly_flags.append("VERY_LARGE_AMOUNT")

    if "refund" in description and amount > 0:
        anomaly_flags.append("REFUND_INFLOW")

    if "salary" in description and amount > 0:
        anomaly_flags.append("SALARY_AS_INCOME")

    enriched = dict(tx)
    enriched.update(
        {
            "category": category,
            "is_unclassified": is_unclassified,
            "anomaly_flags": anomaly_flags,
        }
    )
    return enriched


def assist_bookkeeping(transactions: List[Dict]) -> Dict:
    """
    Run bookkeeping assistance on a batch of transactions.

    Returns:
        {
            "categorized_transactions": [...],
            "unclassified_count": int,
            "anomalies": [ ... ]  # subset of transactions with anomaly flags
        }
    """

    categorized: List[Dict] = []
    anomalies: List[Dict] = []

    for tx in transactions:
        enriched = categorize_transaction(tx)
        categorized.append(enriched)
        if enriched["anomaly_flags"]:
            anomalies.append(enriched)

    unclassified_count = sum(1 for tx in categorized if tx["is_unclassified"])

    return {
        "categorized_transactions": categorized,
        "unclassified_count": unclassified_count,
        "anomalies": anomalies,
    }

