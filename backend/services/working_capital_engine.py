"""
Working capital optimization and simulation engine.
"""

from typing import Dict, List


# ============================================================
# Core Simulation Logic
# ============================================================

def simulate_working_capital(metrics: Dict) -> Dict:
    """
    Build a working capital view and basic optimization recommendations.
    """

    ar_days = float(metrics.get("receivable_days", 0))
    ap_days = float(metrics.get("payable_days", 0))
    inventory_turnover = float(metrics.get("inventory_turnover", 0))
    current_ratio = float(metrics.get("current_ratio", 0))
    working_capital = float(metrics.get("working_capital", 0))

    recommendations: List[str] = []

    # AR recommendations
    if ar_days > 90:
        recommendations.append(
            "Receivable days exceed 90; tighten credit terms and improve collections."
        )
    elif ar_days > 60:
        recommendations.append(
            "Receivable days are elevated; consider early payment incentives."
        )

    # AP recommendations
    if ap_days < 30:
        recommendations.append(
            "Payable days are low; explore supplier negotiations for longer payment terms."
        )

    # Inventory recommendations
    if inventory_turnover < 2:
        recommendations.append(
            "Inventory turnover is low; review slow-moving stock and purchasing policies."
        )

    # Liquidity recommendations
    if current_ratio < 1:
        recommendations.append(
            "Current ratio below 1; liquidity buffer is thin. Prioritize cash preservation."
        )
    elif current_ratio < 1.5:
        recommendations.append(
            "Current ratio is moderate; build an extra cash buffer for resilience."
        )

    simulated_buffer = (
        max(current_ratio * 1.15, current_ratio + 0.2)
        if current_ratio > 0 else 0
    )

    return {
        "ar_days": round(ar_days, 2),
        "ap_days": round(ap_days, 2),
        "inventory_turnover": round(inventory_turnover, 2),
        "liquidity_buffer_current": round(current_ratio, 2),
        "liquidity_buffer_simulated": round(simulated_buffer, 2),
        "working_capital": round(working_capital, 2),
        "recommendations": recommendations,
    }


# ============================================================
# REQUIRED FUNCTION FOR ROUTE IMPORT
# ============================================================

def analyze_working_capital(financial) -> Dict:
    """
    Adapter function used by /analyze route.
    Converts FinancialStatement ORM into metrics-like dict.
    """

    try:
        metrics = {
            "receivable_days": getattr(financial, "receivable_days", 0),
            "payable_days": getattr(financial, "payable_days", 0),
            "inventory_turnover": getattr(financial, "inventory_turnover", 0),
            "current_ratio": (
                (financial.assets / financial.liabilities)
                if getattr(financial, "liabilities", 0) not in [0, None]
                else 0
            ),
            "working_capital": (
                (financial.assets or 0) - (financial.liabilities or 0)
            ),
        }

        return simulate_working_capital(metrics)

    except Exception as e:
        return {
            "working_capital": 0,
            "recommendations": [],
            "error": str(e),
        }
