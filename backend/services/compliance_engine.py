"""
Tax and GST compliance checking engine.

Given normalized GST metrics and revenue, this module generates:
- Compliance warnings
- Compliance score
"""

from __future__ import annotations
from typing import Dict, List


# ============================================================
# Core GST Compliance Logic
# ============================================================

def evaluate_gst_compliance(gst_data: Dict[str, float], revenue: float) -> List[Dict]:
    warnings: List[Dict] = []

    gst_collected = gst_data.get("gst_collected", 0.0)
    gst_paid = gst_data.get("gst_paid", 0.0)
    input_credit = gst_data.get("input_credit", 0.0)
    output_tax = gst_data.get("output_tax", 0.0)

    if revenue > 0:
        effective_rate = gst_collected / revenue

        if effective_rate < 0.05:
            warnings.append({
                "issue_type": "POSSIBLE_UNDER_REPORTING",
                "message": f"Effective GST rate ({effective_rate:.2%}) very low vs revenue.",
                "severity": "High",
            })
        elif effective_rate < 0.12:
            warnings.append({
                "issue_type": "LOW_GST_RATIO",
                "message": f"GST rate ({effective_rate:.2%}) below expected range.",
                "severity": "Medium",
            })

        if effective_rate > 0.30:
            warnings.append({
                "issue_type": "ABNORMALLY_HIGH_GST_RATIO",
                "message": "GST rate unusually high vs revenue.",
                "severity": "Medium",
            })

    net_liability = output_tax - input_credit

    if net_liability < 0 and gst_paid > 0:
        warnings.append({
            "issue_type": "NEGATIVE_NET_LIABILITY",
            "message": "Negative net GST liability but GST paid.",
            "severity": "Medium",
        })

    if net_liability > 0:
        if gst_paid < net_liability * 0.7:
            warnings.append({
                "issue_type": "UNDERPAID_GST",
                "message": "GST paid appears below calculated liability.",
                "severity": "High",
            })
        elif gst_paid > net_liability * 1.3:
            warnings.append({
                "issue_type": "OVERPAID_GST",
                "message": "GST paid appears higher than expected liability.",
                "severity": "Low",
            })

    return warnings


# ============================================================
# REQUIRED FUNCTION FOR ROUTE IMPORT
# ============================================================

def check_compliance(financial) -> Dict:
    """
    Adapter for /analyze route.

    Extracts GST fields from financial model and returns:
    - compliance_score
    - issues
    """

    try:
        gst_data = {
            "gst_collected": float(getattr(financial, "gst_collected", 0)),
            "gst_paid": float(getattr(financial, "gst_paid", 0)),
            "input_credit": float(getattr(financial, "input_credit", 0)),
            "output_tax": float(getattr(financial, "output_tax", 0)),
        }

        revenue = float(getattr(financial, "revenue", 0))

        issues = evaluate_gst_compliance(gst_data, revenue)

        compliance_score = max(0, 100 - (len(issues) * 20))

        return {
            "compliance_score": compliance_score,
            "issues": issues
        }

    except Exception as e:
        return {
            "compliance_score": 0,
            "issues": [],
            "error": str(e)
        }
