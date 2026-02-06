from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import FinancialStatement, RiskScore, InvestorScore
from services.financial_engine import calculate_financial_metrics
from services.risk_engine import calculate_risk_score
from services.investor_engine import calculate_investor_score

router = APIRouter()


@router.post("/investor/{business_id}")
def calculate_investor_readiness(business_id: int, db: Session = Depends(get_db)):

    # ----------------------------
    # 1. Fetch Latest Financial Data
    # ----------------------------
    financial = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.business_id == business_id)
        .order_by(FinancialStatement.created_at.desc())
        .first()
    )

    if not financial:
        raise HTTPException(status_code=404, detail="No financial data found")

    # ----------------------------
    # 2. Calculate Financial Metrics
    # ----------------------------
    metrics = calculate_financial_metrics(financial)

    # ----------------------------
    # 3. Get or Calculate Risk Score
    # ----------------------------
    latest_risk = (
        db.query(RiskScore)
        .filter(RiskScore.business_id == business_id)
        .order_by(RiskScore.created_at.desc())
        .first()
    )

    if latest_risk:
        risk_score_value = latest_risk.score
    else:
        risk_score_value = calculate_risk_score(metrics)

    # ----------------------------
    # 4. Calculate Investor Score
    # ----------------------------
    investor_score_value = calculate_investor_score(metrics, risk_score_value)

    # Categorization
    if investor_score_value >= 80:
        investor_category = "Highly Investment Ready"
    elif investor_score_value >= 60:
        investor_category = "Investment Ready"
    elif investor_score_value >= 40:
        investor_category = "Growth Potential"
    else:
        investor_category = "Not Ready"

    # ----------------------------
    # 5. Save to Database
    # ----------------------------
    investor_record = InvestorScore(
        business_id=business_id,
        score=investor_score_value,
        category=investor_category
    )

    db.add(investor_record)
    db.commit()
    db.refresh(investor_record)

    return {
        "business_id": business_id,
        "investor_score": investor_score_value,
        "category": investor_category,
        "risk_dependency": risk_score_value,
        "metrics_used": metrics
    }
