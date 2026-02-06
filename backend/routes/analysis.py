from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import (
    FinancialStatement,
    RiskScore,
    InvestorScore,
    FraudFlag,
    ESGScore,
    EarlyWarning,
    Business,
)

from services.financial_engine import calculate_financial_metrics
from services.risk_engine import calculate_risk_score
from services.warning_engine import generate_warnings
from services.investor_engine import calculate_investor_score
from services.fraud_engine import detect_fraud
from services.esg_engine import calculate_esg_score
from services.ai_engine import generate_ai_summary
from services.benchmarking_engine import (
    benchmark_against_industry,
    industry_risk_modifier,
)
from services.product_recommendation_engine import recommend_products

# NEW ENGINES
from services.cashflow_engine import calculate_cashflow
from services.forecasting_engine import forecast_financials
from services.working_capital_engine import analyze_working_capital
from services.cost_optimization_engine import optimize_costs
from services.compliance_engine import check_compliance


router = APIRouter()


@router.post("/analyze/{business_id}")
def analyze_business(
    business_id: int,
    lang: str = "en",
    db: Session = Depends(get_db),
):
    try:
        # --------------------------------------------------
        # 1️⃣ Fetch Latest Financial
        # --------------------------------------------------
        financial = (
            db.query(FinancialStatement)
            .filter(FinancialStatement.business_id == business_id)
            .order_by(FinancialStatement.created_at.desc())
            .first()
        )

        if not financial:
            raise HTTPException(status_code=404, detail="No financial data found")

        business = db.query(Business).filter(
            Business.id == financial.business_id
        ).first()

        industry = business.industry if business else "Unknown"

        # --------------------------------------------------
        # 2️⃣ Financial Metrics
        # --------------------------------------------------
        metrics = calculate_financial_metrics(financial)

        # --------------------------------------------------
        # 3️⃣ Risk + Benchmarking
        # --------------------------------------------------
        risk_result = calculate_risk_score(metrics)
        benchmarking = benchmark_against_industry(metrics, industry=industry)
        modifier = industry_risk_modifier(benchmarking)

        base_score = risk_result.get("risk_score", 600)
        adjusted_score = max(300, min(900, base_score + modifier))

        if adjusted_score >= 750:
            risk_category = "Low Risk"
        elif adjusted_score >= 600:
            risk_category = "Medium Risk"
        else:
            risk_category = "High Risk"

        db.add(RiskScore(
            business_id=business_id,
            score=adjusted_score,
            category=risk_category
        ))

        # --------------------------------------------------
        # 4️⃣ Investor Score
        # --------------------------------------------------
        investor_result = calculate_investor_score(metrics, adjusted_score)

        investor_score = investor_result.get("investor_score", 0)
        investor_category = investor_result.get("category", "Unknown")

        db.add(InvestorScore(
            business_id=business_id,
            score=investor_score,
            category=investor_category
        ))

        # --------------------------------------------------
        # 5️⃣ Fraud
        # --------------------------------------------------
        fraud_flags = detect_fraud(financial) or []

        for flag in fraud_flags:
            db.add(FraudFlag(
                business_id=business_id,
                flag_type=flag.get("type", "Anomaly"),
                description=flag.get("message", ""),
                severity=flag.get("severity", "Medium")
            ))

        # --------------------------------------------------
        # 6️⃣ ESG
        # --------------------------------------------------
        esg_result = calculate_esg_score(financial)

        esg_score = esg_result.get("esg_score", 0)
        esg_category = esg_result.get("category", "Neutral")

        db.add(ESGScore(
            business_id=business_id,
            score=esg_score,
            category=esg_category
        ))

        # --------------------------------------------------
        # 7️⃣ Early Warning
        # --------------------------------------------------
        warnings_result = generate_warnings(metrics)
        warnings_list = warnings_result.get("warnings", [])
        survival_score = warnings_result.get("survival_score", 0)

        for w in warnings_list:
            db.add(EarlyWarning(
                business_id=business_id,
                warning_type=w.get("type", "Warning"),
                message=w.get("message", ""),
                severity=w.get("severity", "High")
            ))

        # --------------------------------------------------
        # 8️⃣ Cashflow
        # --------------------------------------------------
        cashflow_data = calculate_cashflow(financial) or {
            "net_cash_flow": financial.revenue - financial.expenses,
            "burn_rate": max(0, financial.expenses - financial.revenue)
        }

        # --------------------------------------------------
        # 9️⃣ ENTERPRISE FORECASTING (NEW ENGINE)
        # --------------------------------------------------
        from services.forecasting_engine import (
            build_time_series_from_rows,
            generate_forecast,
            extract_forecast_signals,
            get_forecast_for_product_recommendation,
        )

        historical_rows = (
            db.query(FinancialStatement)
            .filter(FinancialStatement.business_id == business_id)
            .order_by(FinancialStatement.created_at.asc())
            .all()
        )

        rows = [
            {
                "date": r.created_at,
                "revenue": r.revenue,
                "expenses": r.expenses,
                "assets": r.assets,
                "liabilities": r.liabilities,
            }
            for r in historical_rows
        ]

        forecast_data = {}
        forecast_signals = {}
        product_forecast_metrics = {}

        if len(rows) >= 3:
            try:
                df = build_time_series_from_rows(rows)

                forecast_data = generate_forecast(
                    df,
                    horizon_months=3
                )

                forecast_signals = extract_forecast_signals(forecast_data)

                product_forecast_metrics = (
                    get_forecast_for_product_recommendation(forecast_data)
                )

            except Exception as e:
                forecast_data = {"error": str(e)}

        # --------------------------------------------------
        # 🔟 Working Capital
        # --------------------------------------------------
        working_capital_data = analyze_working_capital(financial) or {
            "working_capital": financial.assets - financial.liabilities
        }

        # --------------------------------------------------
        # 1️⃣1️⃣ Cost Optimization
        # --------------------------------------------------
        cost_data = optimize_costs(metrics) or {
            "optimization_score": 0
        }

        # --------------------------------------------------
        # 1️⃣2️⃣ Compliance
        # --------------------------------------------------
        compliance_data = check_compliance(financial) or {
            "compliance_score": 0,
            "issues": []
        }

        # --------------------------------------------------
        # 1️⃣3️⃣ Product Recommendations
        # --------------------------------------------------
        product_data = recommend_products(
            adjusted_score,
            metrics,
            forecast_data=product_forecast_metrics
        ) or []

        # --------------------------------------------------
        # 1️⃣4️⃣ AI Summary
        # --------------------------------------------------
        ai_recommendations = generate_ai_summary(
            metrics=metrics,
            risk_data=risk_result,
            investor_data=investor_result,
            esg_data=esg_result,
            warnings=warnings_result,
            fraud_flags=fraud_flags,
            language=lang,
        )

        ai_summary_text = "No AI summary available."
        if isinstance(ai_recommendations, dict):
            lines = []
            for key in [
                "strategic_actions",
                "cost_optimization",
                "liquidity_improvements",
                "funding_recommendations",
            ]:
                for item in ai_recommendations.get(key, []):
                    lines.append(f"- {item}")
            if lines:
                ai_summary_text = "\n".join(lines)

        db.commit()

        # --------------------------------------------------
        # 🚀 FINAL RESPONSE
        # --------------------------------------------------
        return {
            "metrics": metrics,
            "industry": industry,

            "risk": {
                "score": adjusted_score,
                "category": risk_category,
            },

            "investor": {
                "score": investor_score,
                "category": investor_category,
            },

            "esg": {
                "score": esg_score,
                "category": esg_category,
            },

            "fraud_flags": fraud_flags,
            "warnings": warnings_list,
            "survival_score": survival_score,

            "cashflow": cashflow_data,
            "forecast": forecast_data,
            "forecast_signals": forecast_signals,
            "working_capital": working_capital_data,
            "cost_optimization": cost_data,
            "compliance": compliance_data,
            "benchmarking": benchmarking,
            "product_recommendations": product_data,

            "ai_summary": ai_summary_text,
            "ai_recommendations": ai_recommendations,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )
