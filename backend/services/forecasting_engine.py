"""
Unified Forecasting Engine
Compatible with all existing route imports
"""

from typing import Dict, List
from dataclasses import dataclass
import numpy as np
import pandas as pd


# ============================================================
# Exception
# ============================================================

@dataclass
class ForecastingError(Exception):
    code: str
    message: str


# ============================================================
# Time-Series Builder
# ============================================================

def build_time_series_from_rows(rows: List[Dict]) -> pd.DataFrame:
    if not rows:
        raise ForecastingError("NO_DATA", "No historical data provided")

    df = pd.DataFrame(rows)

    if "date" not in df.columns:
        raise ForecastingError("MISSING_DATE", "date column required")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")

    return df


# ============================================================
# Simple Linear Model
# ============================================================

def _linear_model(series: pd.Series, horizon: int):
    y = series.values.astype(float)
    x = np.arange(len(y))

    if len(y) < 2:
        return list(y), [float(y[-1])] * horizon, 0.5

    slope, intercept = np.polyfit(x, y, 1)
    future_x = np.arange(len(y), len(y) + horizon)
    forecast = slope * future_x + intercept
    forecast = np.maximum(forecast, 0)

    return list(y), list(forecast), 0.7


# ============================================================
# Route-Compatible Forecast (Used in /analyze)
# ============================================================

def forecast_financials(metrics: Dict, horizon: int = 3) -> Dict:
    revenue = float(metrics.get("revenue", 0))
    expenses = float(metrics.get("expenses", 0))

    projected_revenue = revenue * 1.05
    projected_expenses = expenses * 1.04

    return {
        "projected_revenue": round(projected_revenue, 2),
        "projected_expenses": round(projected_expenses, 2),
        "projected_cashflow": round(projected_revenue - projected_expenses, 2),
        "confidence": 0.7,
    }


# ============================================================
# Advanced Generator (Used by forecasting route)
# ============================================================

def generate_forecast(df: pd.DataFrame, horizon_months: int = 3) -> Dict:

    df["period"] = df["date"].dt.to_period("M").astype(str)

    monthly = (
        df.groupby("period")[["revenue", "expenses"]]
        .sum()
        .reset_index()
    )

    rev_series = pd.Series(monthly["revenue"].values)
    exp_series = pd.Series(monthly["expenses"].values)
    cash_series = rev_series - exp_series

    _, rev_future, _ = _linear_model(rev_series, horizon_months)
    _, exp_future, _ = _linear_model(exp_series, horizon_months)
    _, cash_future, _ = _linear_model(cash_series, horizon_months)

    return {
        "revenue_forecast": rev_future,
        "expense_forecast": exp_future,
        "cashflow_forecast": cash_future,
    }


# ============================================================
# Forecast Signal Extractor (REQUIRED BY ROUTE)
# ============================================================

def extract_forecast_signals(forecast: Dict) -> Dict:
    cashflow = forecast.get("cashflow_forecast", [])

    negative_months = sum(1 for v in cashflow if v < 0)

    trend = "positive"
    if sum(cashflow) < 0:
        trend = "negative"

    return {
        "negative_cashflow_months": negative_months,
        "trend_direction": trend,
        "forecast_confidence": 0.7,
    }


# ============================================================
# Product Recommendation Extractor
# ============================================================

def get_forecast_for_product_recommendation(forecast: Dict) -> Dict:

    cashflow = forecast.get("cashflow_forecast", [])

    if not cashflow:
        return {
            "liquidity_forecast_score": 50,
            "average_projected_cashflow": 0,
        }

    avg_cf = np.mean(cashflow)

    if avg_cf >= 0:
        score = 80
    elif avg_cf >= -10000:
        score = 60
    else:
        score = 30

    return {
        "liquidity_forecast_score": score,
        "average_projected_cashflow": float(avg_cf),
    }
