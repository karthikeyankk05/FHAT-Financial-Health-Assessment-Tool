"""
Cash Flow Modelling Engine

Supports:
1️⃣ Historical time-series cashflow computation
2️⃣ Single financial row quick cashflow calculation
3️⃣ Burn rate analysis
4️⃣ Liquidity ratio tracking
"""

from __future__ import annotations

from typing import Dict, List
import pandas as pd


# ============================================================
# 1️⃣ HISTORICAL CASHFLOW (TIME SERIES)
# ============================================================

def compute_cashflow_metrics(df: pd.DataFrame) -> Dict:
    """
    Compute high-level cash flow metrics from historical time series.

    Expected columns:
        - date
        - revenue
        - expenses
        - assets
        - liabilities
    """

    required_cols = {"date", "revenue", "expenses", "assets", "liabilities"}
    missing = required_cols - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if df.empty:
        return {
            "monthly_net_cash_flow": [],
            "rolling_liquidity_ratio": [],
            "burn_rate": 0.0,
        }

    df_sorted = df.sort_values("date").copy()
    df_sorted["period"] = df_sorted["date"].dt.to_period("M").astype(str)

    grouped = (
        df_sorted.groupby("period")[["revenue", "expenses", "assets", "liabilities"]]
        .sum()
        .reset_index()
    )

    grouped["net_cash_flow"] = grouped["revenue"] - grouped["expenses"]

    grouped["liquidity_ratio"] = grouped.apply(
        lambda row: (
            row["assets"] / row["liabilities"]
            if row["liabilities"] > 0 else 0
        ),
        axis=1,
    )

    monthly_net = [
        {
            "period": row["period"],
            "net_cash_flow": float(row["net_cash_flow"])
        }
        for _, row in grouped.iterrows()
    ]

    liquidity_series = [
        {
            "period": row["period"],
            "liquidity_ratio": float(row["liquidity_ratio"])
        }
        for _, row in grouped.iterrows()
    ]

    negative_months = grouped[grouped["net_cash_flow"] < 0]["net_cash_flow"]
    burn_rate = (
        float(abs(negative_months.mean()))
        if not negative_months.empty
        else 0.0
    )

    return {
        "monthly_net_cash_flow": monthly_net,
        "rolling_liquidity_ratio": liquidity_series,
        "burn_rate": round(burn_rate, 2),
    }


# ============================================================
# 2️⃣ SINGLE ROW CASHFLOW (FOR /analyze ROUTE)
# ============================================================

def calculate_cashflow(financial) -> Dict:
    """
    Quick cashflow calculation for latest financial record.

    Used in main analysis route when only one record is available.
    """

    revenue = float(financial.revenue or 0)
    expenses = float(financial.expenses or 0)
    assets = float(financial.assets or 0)
    liabilities = float(financial.liabilities or 0)

    net_cash_flow = revenue - expenses
    burn_rate = max(0, expenses - revenue)

    liquidity_ratio = (
        assets / liabilities if liabilities > 0 else 0
    )

    return {
        "net_cash_flow": round(net_cash_flow, 2),
        "burn_rate": round(burn_rate, 2),
        "liquidity_ratio": round(liquidity_ratio, 3),
    }
