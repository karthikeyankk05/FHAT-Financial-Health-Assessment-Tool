import json
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database import get_db
from models import Business, GSTFiling, ComplianceIssue, FinancialStatement
from services.gst_service import (
    parse_gst_from_json_bytes,
    parse_gst_from_csv_file,
    validate_gst_consistency,
    GSTParsingError,
    GSTValidationError,
)
from services.compliance_engine import evaluate_gst_compliance


router = APIRouter()


def _error_response(status_code: int, error_code: str, message: str, details: str = "") -> JSONResponse:
    """
    Build a structured error response for GST routes.
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


@router.post("/gst/upload/{business_id}")
async def upload_gst_filing(
    business_id: int,
    file: UploadFile = File(...),
    period: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Upload GST filing data from JSON or CSV, validate it, and persist to the database.

    Also runs the compliance engine to generate GST-related compliance warnings.
    """

    try:
        if not file.filename.lower().endswith((".json", ".csv")):
            return _error_response(
                status_code=400,
                error_code="INVALID_FILE_TYPE",
                message="Only JSON and CSV files are allowed for GST import.",
                details=f"Received: {file.filename}",
            )

        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return _error_response(
                status_code=404,
                error_code="BUSINESS_NOT_FOUND",
                message="No business found for the given business_id.",
                details=f"business_id={business_id}",
            )

        # Parse GST metrics
        try:
            if file.filename.lower().endswith(".json"):
                raw_bytes = await file.read()
                gst_data = parse_gst_from_json_bytes(raw_bytes)
            else:
                gst_data = parse_gst_from_csv_file(file.file)
        except GSTParsingError as exc:
            return _error_response(
                status_code=400,
                error_code="GST_PARSE_ERROR",
                message="Failed to parse GST filing data.",
                details=str(exc),
            )

        # Consistency validation
        try:
            validate_gst_consistency(gst_data)
        except GSTValidationError as exc:
            return _error_response(
                status_code=400,
                error_code="GST_VALIDATION_ERROR",
                message="GST filing failed internal consistency checks.",
                details=str(exc),
            )

        # Persist GST filing
        filing = GSTFiling(
            business_id=business_id,
            gst_collected=gst_data["gst_collected"],
            gst_paid=gst_data["gst_paid"],
            input_credit=gst_data["input_credit"],
            output_tax=gst_data["output_tax"],
            period=period,
            tax_metadata=json.dumps({"source_filename": file.filename}),
        )
        db.add(filing)

        # Fetch latest revenue for compliance engine (if available)
        latest_financial: Optional[FinancialStatement] = (
            db.query(FinancialStatement)
            .filter(FinancialStatement.business_id == business_id)
            .order_by(FinancialStatement.created_at.desc())
            .first()
        )
        revenue = latest_financial.revenue if latest_financial else 0.0

        compliance_warnings = evaluate_gst_compliance(gst_data, revenue)

        for warning in compliance_warnings:
            db.add(
                ComplianceIssue(
                    business_id=business_id,
                    issue_type=warning.get("issue_type", "GST_COMPLIANCE"),
                    message=warning.get("message", ""),
                    severity=warning.get("severity", "Medium"),
                )
            )

        db.commit()
        db.refresh(filing)

        return {
            "status": "success",
            "data": {
                "business_id": business_id,
                "gst_filing_id": filing.id,
                "gst": gst_data,
                "compliance_warnings": compliance_warnings,
            },
        }

    except Exception as exc:  # pragma: no cover - defensive
        return _error_response(
            status_code=500,
            error_code="GST_UPLOAD_INTERNAL_ERROR",
            message="Unexpected error while processing GST filing upload.",
            details=str(exc),
        )

