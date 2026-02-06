"""
Industry-specific benchmarking engine.

Provides mock benchmark ranges for key metrics across industries and
returns percentile-style positioning for a given business.

Industries covered (mock data):
    - manufacturing
    - retail
    - agriculture
    - services
    - logistics
    - e-commerce
"""

from __future__ import annotations

from typing import Dict


_BENCHMARKS = {
    "manufacturing": {
        "gross_margin": (20, 35, 50),
        "debt_ratio": (0.3, 0.6, 0.9),
        "working_capital": (-0.1, 0.1, 0.3),
    },
    "retail": {
        "gross_margin": (15, 30, 45),
        "debt_ratio": (0.2, 0.5, 0.8),
        "working_capital": (-0.05, 0.05, 0.2),
    },
    "agriculture": {
        "gross_margin": (10, 25, 40),
        "debt_ratio": (0.25, 0.55, 0.85),
        "working_capital": (-0.15, 0.05, 0.25),
    },
    "services": {
        "gross_margin": (30, 45, 60),
        "debt_ratio": (0.1, 0.3, 0.6),
        "working_capital": (0.0, 0.15, 0.35),
    },
    "logistics": {
        "gross_margin": (15, 25, 40),
        "debt_ratio": (0.3, 0.6, 0.9),
        "working_capital": (-0.05, 0.1, 0.25),
    },
    "e-commerce": {
        "gross_margin": (20, 35, 55),
        "debt_ratio": (0.2, 0.4, 0.7),
        "working_capital": (-0.1, 0.0, 0.2),
    },
}

_DEFAULT_BENCHMARK = {
    "gross_margin": (15, 30, 50),
    "debt_ratio": (0.2, 0.5, 0.8),
    "working_capital": (-0.1, 0.05, 0.25),
}


def _normalize_industry(industry: str) -> str:
    return (industry or "").strip().lower()


def _map_to_percentile(value: float, p25: float, p50: float, p75: float) -> float:
    """
    Map a numeric value to a rough percentile score using simple anchors.
    """

    if value <= p25:
        return 25.0
    if value >= p75:
        return 90.0
    if value == p50:
        return 50.0

    if value < p50:
        # interpolate between 25 and 50
        span = p50 - p25 or 1.0
        return 25.0 + (value - p25) / span * 25.0

    # interpolate between 50 and 90
    span = p75 - p50 or 1.0
    return 50.0 + (value - p50) / span * 40.0


def benchmark_against_industry(metrics: Dict, industry: str) -> Dict:
    """
    Compare a business' metrics to industry benchmarks and return percentile ranks.

    Args:
        metrics: Output dict from `calculate_financial_metrics`.
        industry: Business industry string.

    Returns:
        {
          "industry": "...",
          "used_default": bool,
          "gross_margin_percentile": float,
          "debt_ratio_percentile": float,
          "working_capital_percentile": float
        }
    """

    normalized = _normalize_industry(industry)
    bench = _BENCHMARKS.get(normalized, _DEFAULT_BENCHMARK)

    gm = float(metrics.get("gross_margin", 0))
    # Approximate debt ratio using debt_to_equity -> debt / (debt + equity)
    de = float(metrics.get("debt_to_equity", 0))
    debt_ratio = de / (1 + de) if de >= 0 else 0.0

    # Normalize working capital by assets proxy (if available)
    # Fallback: interpret working_capital as % of revenue proxy using margins.
    wc = float(metrics.get("working_capital", 0))
    # Assume revenue proxy ~ working_capital / (net_margin% / 100 + 1) for rough normalization
    rev_proxy = abs(wc) / ((metrics.get("net_margin", 0) / 100.0) + 1.0) if wc != 0 else 1.0
    working_capital_ratio = wc / rev_proxy if rev_proxy else 0.0

    gm_p25, gm_p50, gm_p75 = bench["gross_margin"]
    dr_p25, dr_p50, dr_p75 = bench["debt_ratio"]
    wc_p25, wc_p50, wc_p75 = bench["working_capital"]

    gm_pct = _map_to_percentile(gm, gm_p25, gm_p50, gm_p75)
    dr_pct = _map_to_percentile(debt_ratio, dr_p25, dr_p50, dr_p75)
    wc_pct = _map_to_percentile(working_capital_ratio, wc_p25, wc_p50, wc_p75)

    return {
        "industry": normalized or "unknown",
        "used_default": normalized not in _BENCHMARKS,
        "gross_margin_percentile": round(gm_pct, 1),
        "debt_ratio_percentile": round(dr_pct, 1),
        "working_capital_percentile": round(wc_pct, 1),
    }


def industry_risk_modifier(benchmark_summary: Dict) -> int:
    """
    Calculate a risk-score modifier (delta) based on industry benchmarking.

    Returns:
        Negative value -> risk score bonus (better than peers)
        Positive value -> risk score penalty (worse than peers)
    """

    gm_pct = benchmark_summary.get("gross_margin_percentile", 50.0)
    dr_pct = benchmark_summary.get("debt_ratio_percentile", 50.0)
    wc_pct = benchmark_summary.get("working_capital_percentile", 50.0)

    modifier = 0

    if gm_pct < 30:
        modifier += 30
    elif gm_pct > 70:
        modifier -= 20

    if dr_pct > 70:
        modifier += 40
    elif dr_pct < 30:
        modifier -= 20

    if wc_pct < 30:
        modifier += 20
    elif wc_pct > 70:
        modifier -= 10

    # Clamp to a reasonable range
    return max(-80, min(80, modifier))

