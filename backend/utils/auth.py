"""
Lightweight role-based access control helpers.

This module does not implement full authentication; instead, it provides
dependencies that interpret a caller's role from headers and allows
endpoint-level RBAC decisions without breaking existing clients.
"""

from __future__ import annotations

from typing import List

from fastapi import Header, HTTPException, status, Depends


async def get_current_role(x_user_role: str | None = Header(default=None)) -> str:
    """
    Extract the current user's role from the `X-User-Role` header.

    For backwards compatibility, if the header is missing, we assume
    a `business_owner` role. This can be tightened in a real auth setup.
    """

    if not x_user_role:
        return "business_owner"
    return x_user_role.lower()


def require_roles(allowed_roles: List[str]):
    """
    Dependency factory that enforces the current role is within `allowed_roles`.

    Example:
        @router.get("/secure", dependencies=[Depends(require_roles(["admin", "analyst"]))])
    """

    async def _checker(role: str = Depends(get_current_role)) -> None:
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions for this operation.",
            )

    return _checker

