from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import FinancialStatement, FraudFlag
from services.fraud_engine import detect_fraud

router = APIRouter()


@router.post("/fraud/{business_id}")
def analyze_fraud(business_id: int, db: Session = Depends(get_db)):

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
    # 2. Run Fraud Detection
    # ----------------------------
    fraud_flags = detect_fraud(financial)

    saved_flags = []

    for flag in fraud_flags:

        # Basic severity classification
        if "Expense" in flag:
            severity = "High"
        elif "Receivables" in flag:
            severity = "Medium"
        else:
            severity = "Low"

        fraud_record = FraudFlag(
            business_id=business_id,
            flag_type="Financial Anomaly",
            description=flag,
            severity=severity
        )

        db.add(fraud_record)
        saved_flags.append({
            "description": flag,
            "severity": severity
        })

    db.commit()

    return {
        "business_id": business_id,
        "fraud_flags_detected": saved_flags,
        "total_flags": len(saved_flags)
    }
