from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models import FinancialStatement, Business
from services.financial_engine import calculate_financial_metrics
from services.cashflow_engine import compute_cashflow_metrics
from services.working_capital_engine import simulate_working_capital
from services.forecasting_engine import (
    build_time_series_from_rows,
    generate_forecast,
    extract_forecast_signals,
    get_forecast_for_product_recommendation,
    ForecastingError,
)


router = APIRouter()


def _error_response(status_code: int, error_code: str, message: str, details: str = "") -> JSONResponse:
    """
    Build a structured error response for forecasting routes.
    """

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "error_code": error_code,
            "message": message,
            "details": details,
        },
    )


@router.get("/forecast/{business_id}")
def forecast_business(
    business_id: int,
    horizon_months: int = Query(6, ge=3, le=6, description="Forecast horizon in months (3–6)."),
    db: Session = Depends(get_db),
):
    """
    Generate forward-looking financial forecasts and cash-flow intelligence for a business.

    Combines:
        - Linear-trend forecast for revenue, expenses, net cash flow
        - Cash-flow aggregates (net cash, liquidity ratios, burn rate)
        - Working capital optimization view for the latest period
    """

    try:
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return _error_response(
                status_code=404,
                error_code="BUSINESS_NOT_FOUND",
                message="No business found for the given business_id.",
                details=f"business_id={business_id}",
            )

        # Pull historical financial statements
        statements = (
            db.query(FinancialStatement)
            .filter(FinancialStatement.business_id == business_id)
            .order_by(FinancialStatement.created_at.asc())
            .all()
        )

        if not statements:
            return _error_response(
                status_code=404,
                error_code="NO_FINANCIAL_DATA",
                message="No financial statements available for forecasting.",
                details=f"business_id={business_id}",
            )

        rows = [
            {
                "date": fs.created_at,
                "revenue": fs.revenue,
                "expenses": fs.expenses,
                "assets": fs.assets,
                "liabilities": fs.liabilities,
            }
            for fs in statements
        ]

        try:
            ts_df = build_time_series_from_rows(rows)
            forecast_payload = generate_forecast(
                ts_df,
                horizon_months=horizon_months,
                enable_backtesting=True,
                enable_drift_monitoring=True,
            )
        except ForecastingError as exc:
            # Map known forecasting errors to 400-series codes.
            return _error_response(
                status_code=400,
                error_code=exc.code,
                message="Forecasting failed.",
                details=str(exc),
            )

        # Cash-flow analytics
        cashflow_metrics = compute_cashflow_metrics(ts_df)

        # Latest working capital view (using most recent statement)
        latest_statement: FinancialStatement = statements[-1]
        latest_metrics = calculate_financial_metrics(latest_statement)
        working_capital_view = simulate_working_capital(latest_metrics)

        # Predictive early warning, using forecast as input
        from services.warning_engine import generate_warnings  # local import to avoid cycles

        predictive_warnings = generate_warnings(
            latest_metrics,
            forecast_summary=forecast_payload,
            risk_trend=None,
        )
        
        # Extract forecast signals for integration
        forecast_signals = extract_forecast_signals(forecast_payload)
        product_forecast_insights = get_forecast_for_product_recommendation(forecast_payload)

        return {
            "status": "success",
            "data": {
                "forecast_horizon_months": horizon_months,
                "forecast": forecast_payload,
                "cashflow": cashflow_metrics,
                "working_capital": working_capital_view,
                "predictive_warnings": predictive_warnings,
                "forecast_signals": forecast_signals,
                "product_recommendation_insights": product_forecast_insights,
            },
        }

    except Exception as exc:  # pragma: no cover - defensive
        return _error_response(
            status_code=500,
            error_code="FORECAST_INTERNAL_ERROR",
            message="Unexpected error while generating forecast.",
            details=str(exc),
        )

