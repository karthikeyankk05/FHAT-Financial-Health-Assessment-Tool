from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import FinancialStatement, RiskScore
from services.financial_engine import calculate_financial_metrics
from services.risk_engine import calculate_risk_score

router = APIRouter()


@router.post("/risk/{business_id}")
def calculate_business_risk(business_id: int, db: Session = Depends(get_db)):

    # Get latest financial statement
    financial = (
        db.query(FinancialStatement)
        .filter(FinancialStatement.business_id == business_id)
        .order_by(FinancialStatement.created_at.desc())
        .first()
    )

    if not financial:
        raise HTTPException(status_code=404, detail="No financial data found")

    # Calculate financial metrics
    metrics = calculate_financial_metrics(financial)

    # Calculate risk score
    risk_score_value = calculate_risk_score(metrics)

    # Categorize risk
    if risk_score_value >= 750:
        risk_category = "Low Risk"
    elif risk_score_value >= 600:
        risk_category = "Medium Risk"
    else:
        risk_category = "High Risk"

    # Save to database
    risk_record = RiskScore(
        business_id=business_id,
        score=risk_score_value,
        category=risk_category
    )

    db.add(risk_record)
    db.commit()
    db.refresh(risk_record)

    return {
        "business_id": business_id,
        "risk_score": risk_score_value,
        "category": risk_category,
        "metrics_used": metrics
    }
