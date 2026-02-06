import pandas as pd
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import FinancialStatement, Business

router = APIRouter()


# Required columns for a minimal upload.
# Other fields (receivables, payables, inventory, debt) are treated as optional
# and will default to 0. This makes it easier to work with simpler CSV files.
REQUIRED_COLUMNS = [
    "revenue",
    "expenses",
    "assets",
    "liabilities",
]


@router.post("/upload/{business_id}")
async def upload_financial_file(
    business_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # Validate file type
    if not file.filename.endswith((".csv", ".xlsx")):
        raise HTTPException(status_code=400, detail="Only CSV and XLSX files allowed.")

    try:
        # Read file
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file.file)
        else:
            df = pd.read_excel(file.file)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"File parsing error: {str(e)}")

    # Normalize column names
    df.columns = [col.strip().lower() for col in df.columns]

    # Validate required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {missing_cols}"
        )

    # Take first row (MVP assumption: single financial summary row)
    data = df.iloc[0]

    # Check if business exists
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        # For this MVP, if the business does not exist yet, create a simple
        # placeholder business record so uploads work out of the box.
        business = Business(
            id=business_id,
            name=f"Business {business_id}",
            industry="Unknown"
        )
        db.add(business)
        db.commit()
        db.refresh(business)

    # Create FinancialStatement record
    financial_entry = FinancialStatement(
        business_id=business_id,
        revenue=float(data["revenue"]),
        expenses=float(data["expenses"]),
        assets=float(data["assets"]),
        liabilities=float(data["liabilities"]),
        receivables=float(data.get("receivables", 0)),
        payables=float(data.get("payables", 0)),
        inventory=float(data.get("inventory", 0)),
        debt=float(data.get("debt", 0))
    )

    db.add(financial_entry)
    db.commit()
    db.refresh(financial_entry)

    return {
        "message": "File uploaded successfully",
        "financial_statement_id": financial_entry.id
    }
