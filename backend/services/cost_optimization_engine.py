"""
Cost Optimization Engine

Provides:
- Expense efficiency scoring
- Cost structure analysis
- Optimization recommendations
"""

from typing import Dict, List


# ============================================================
# Core Cost Logic
# ============================================================

def analyze_cost_structure(metrics: Dict) -> Dict:
    """
    Analyze cost ratios and return optimization insights.
    """

    revenue = float(metrics.get("revenue", 0))
    expenses = float(metrics.get("expenses", 0))

    if revenue <= 0:
        return {
            "cost_ratio": 0,
            "optimization_score": 0,
            "recommendations": ["Revenue data insufficient for cost analysis."]
        }

    cost_ratio = expenses / revenue

    recommendations: List[str] = []

    if cost_ratio > 0.8:
        recommendations.append("Expenses exceed 80% of revenue. Immediate cost rationalization required.")
    elif cost_ratio > 0.6:
        recommendations.append("Cost structure is moderately heavy. Explore supplier renegotiation.")
    elif cost_ratio > 0.4:
        recommendations.append("Cost structure healthy but optimization opportunities exist.")
    else:
        recommendations.append("Strong cost efficiency. Maintain current discipline.")

    # Optimization score (higher is better)
    optimization_score = max(0, min(100, int((1 - cost_ratio) * 100)))

    return {
        "cost_ratio": round(cost_ratio, 2),
        "optimization_score": optimization_score,
        "recommendations": recommendations,
    }


# ============================================================
# REQUIRED FUNCTION FOR ROUTE IMPORT
# ============================================================

def optimize_costs(metrics: Dict) -> Dict:
    """
    Adapter used by /analyze route.
    """

    try:
        return analyze_cost_structure(metrics)

    except Exception as e:
        return {
            "cost_ratio": 0,
            "optimization_score": 0,
            "recommendations": [],
            "error": str(e),
        }
