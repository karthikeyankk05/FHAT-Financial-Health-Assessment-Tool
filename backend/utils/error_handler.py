"""
Centralised API error handling utilities.

Provides:
    - Standardised error response format
    - Optional logging hook
    - Abstraction layer so routes don't leak stack traces
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi.responses import JSONResponse


logger = logging.getLogger("fhat.api")


def api_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: Optional[str] = "",
) -> JSONResponse:
    """
    Build a production-safe error response object and log the event.

    This hides internal stack traces from the caller while still recording
    details server-side.
    """

    log_msg = f"[{error_code}] {message}"
    if details:
        log_msg += f" | details={details}"

    if status_code >= 500:
        logger.error(log_msg)
    else:
        logger.warning(log_msg)

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "error_code": error_code,
            "message": message,
            "details": details or "",
        },
    )

