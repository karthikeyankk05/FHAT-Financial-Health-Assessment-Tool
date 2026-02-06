from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import FinancialStatement, ESGScore
from services.esg_engine import calculate_esg_score

router = APIRouter()


@router.post("/esg/{business_id}")
def calculate_esg(business_id: int, db: Session = Depends(get_db)):

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
    # 2. Calculate ESG Score
    # ----------------------------
    esg_score_value = calculate_esg_score(financial)

    # Categorization
    if esg_score_value >= 80:
        esg_category = "Sustainable Leader"
    elif esg_score_value >= 60:
        esg_category = "Responsible"
    elif esg_score_value >= 40:
        esg_category = "Moderate"
    else:
        esg_category = "Needs Improvement"

    # ----------------------------
    # 3. Save to Database
    # ----------------------------
    esg_record = ESGScore(
        business_id=business_id,
        score=esg_score_value,
        category=esg_category
    )

    db.add(esg_record)
    db.commit()
    db.refresh(esg_record)

    return {
        "business_id": business_id,
        "esg_score": esg_score_value,
        "category": esg_category
    }
