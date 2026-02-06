from datetime import datetime
import json
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import BankSync, Business
from services.banking_service import fetch_banking_data, BankingAPIError


router = APIRouter()


def _error_response(status_code: int, error_code: str, message: str, details: str = "") -> JSONResponse:
    """
    Build a consistent structured error response for banking routes.
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


class BankingSyncRequest(BaseModel):
    """
    Request body for syncing banking data from a mock provider.
    """

    provider: str = Field(..., description="Mock bank identifier, e.g., 'bank1' or 'bank2'.")
    token: str = Field(..., description="Mock API token used for authentication.")
    simulate: Optional[str] = Field(
        default=None,
        description="Optional simulation mode: 'timeout', 'invalid_credentials', 'rate_limit', 'network_failure'.",
    )


@router.post("/banking/sync/{business_id}")
def sync_banking_data(
    business_id: int,
    payload: BankingSyncRequest,
    db: Session = Depends(get_db),
):
    """
    Pull account summary and transaction history from a mock banking provider
    and persist the snapshot to the `bank_syncs` table.

    Supports simulation flags for:
        - API timeout
        - Invalid credentials
        - Rate limiting
        - Network failure
    """

    try:
        # Business existence check
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            return _error_response(
                status_code=404,
                error_code="BUSINESS_NOT_FOUND",
                message="No business found for the given business_id.",
                details=f"business_id={business_id}",
            )

        try:
            banking_data = fetch_banking_data(
                provider=payload.provider,
                token=payload.token,
                simulate=payload.simulate,  # type: ignore[arg-type]
            )
        except BankingAPIError as exc:
            code = exc.code
            status_map = {
                "TIMEOUT": 504,
                "INVALID_CREDENTIALS": 401,
                "RATE_LIMITED": 429,
                "NETWORK_FAILURE": 502,
                "UNSUPPORTED_PROVIDER": 400,
            }
            status = status_map.get(code, 502)
            return _error_response(
                status_code=status,
                error_code=code,
                message="Banking provider call failed.",
                details=str(exc),
            )

        account_balance = float(banking_data["account_balance"])
        transactions = banking_data["transactions"]

        # Persist snapshot
        sync = BankSync(
            business_id=business_id,
            provider=banking_data["provider"],
            account_balance=account_balance,
            transactions_json=json.dumps(transactions),
            last_sync_time=datetime.utcnow(),
        )
        db.add(sync)
        db.commit()
        db.refresh(sync)

        return {
            "status": "success",
            "data": {
                "business_id": business_id,
                "provider": sync.provider,
                "account_balance": sync.account_balance,
                "transactions_count": len(transactions),
                "last_sync_time": sync.last_sync_time.isoformat(),
            },
        }

    except Exception as exc:  # pragma: no cover - defensive
        return _error_response(
            status_code=500,
            error_code="BANKING_SYNC_INTERNAL_ERROR",
            message="Unexpected error while syncing banking data.",
            details=str(exc),
        )

