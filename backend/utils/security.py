"""
Security utilities (hashing, password handling).

Uses bcrypt for password hashing / verification.
"""

from __future__ import annotations

import bcrypt  # type: ignore[import]


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    """

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    """

    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

