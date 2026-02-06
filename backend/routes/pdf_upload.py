from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Business, FinancialStatement
from services.pdf_parser import parse_pdf_financials, PDFParsingError


router = APIRouter()


def _error_response(status_code: int, error_code: str, message: str, details: str = "") -> JSONResponse:
    """
    Build a consistent structured error response for all new routes.
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


@router.post("/upload/pdf/{business_id}")
async def upload_financial_pdf(
    business_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a text-based PDF financial statement and persist a FinancialStatement row.

    The PDF is parsed for high-level financial metrics:
        - revenue
        - expenses
        - assets
        - liabilities
        - inventory
    """

    try:
        if not file.filename.lower().endswith(".pdf"):
            return _error_response(
                status_code=400,
                error_code="INVALID_FILE_TYPE",
                message="Only PDF files are allowed.",
                details=f"Received: {file.filename}",
            )

        # Ensure business exists
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return _error_response(
                status_code=404,
                error_code="BUSINESS_NOT_FOUND",
                message="No business found for the given business_id.",
                details=f"business_id={business_id}",
            )

        try:
            parsed = parse_pdf_financials(file)
        except PDFParsingError as exc:
            return _error_response(
                status_code=400,
                error_code="PDF_PARSE_ERROR",
                message="Failed to extract financial fields from PDF.",
                details=str(exc),
            )

        # Create financial statement using PDF values
        financial_entry = FinancialStatement(
            business_id=business_id,
            revenue=float(parsed["revenue"]),
            expenses=float(parsed["expenses"]),
            assets=float(parsed["assets"]),
            liabilities=float(parsed["liabilities"]),
            receivables=0.0,
            payables=0.0,
            inventory=float(parsed.get("inventory", 0.0)),
            debt=0.0,
        )

        db.add(financial_entry)
        db.commit()
        db.refresh(financial_entry)

        return {
            "status": "success",
            "data": {
                "business_id": business_id,
                "financial_statement_id": financial_entry.id,
                "source": "pdf",
            },
        }

    except Exception as exc:  # pragma: no cover - defensive catch-all
        return _error_response(
            status_code=500,
            error_code="PDF_UPLOAD_INTERNAL_ERROR",
            message="Unexpected error while processing PDF upload.",
            details=str(exc),
        )

