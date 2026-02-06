"""
Mock banking service integration layer.

This module simulates two external banking APIs:
    - BankOne: account summary + transactions
    - BankTwo: account summary + transactions

It supports deterministic simulation of:
    - API timeout
    - Invalid credentials
    - Rate limiting
    - Generic network failure
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Literal, Optional, Tuple


SimulationMode = Optional[Literal["timeout", "invalid_credentials", "rate_limit", "network_failure"]]


@dataclass
class BankingAPIError(Exception):
    """
    Domain-specific error raised when simulated banking APIs fail.
    """

    code: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.code}: {self.message}"


def _simulate_failure(simulate: SimulationMode) -> None:
    """
    Raise a BankingAPIError based on the simulation mode, if set.
    """

    if simulate is None:
        return

    if simulate == "timeout":
        raise BankingAPIError("TIMEOUT", "Banking API request timed out.")
    if simulate == "invalid_credentials":
        raise BankingAPIError("INVALID_CREDENTIALS", "Invalid banking API token.")
    if simulate == "rate_limit":
        raise BankingAPIError("RATE_LIMITED", "Banking API rate limit exceeded.")
    if simulate == "network_failure":
        raise BankingAPIError("NETWORK_FAILURE", "Failed to reach banking API.")


def _mock_bank_one(token: str, simulate: SimulationMode) -> Tuple[float, List[Dict]]:
    """
    Simulate external BankOne APIs for account summary and transaction history.
    """

    _simulate_failure(simulate)

    if not token or not token.startswith("bank1_"):
        raise BankingAPIError("INVALID_CREDENTIALS", "BankOne token is invalid.")

    balance = 250_000.0
    base_time = datetime.utcnow()

    transactions = [
        {
            "id": "tx_1001",
            "amount": -15000.0,
            "currency": "INR",
            "description": "Monthly Office Rent",
            "timestamp": (base_time - timedelta(days=3)).isoformat(),
        },
        {
            "id": "tx_1002",
            "amount": -55000.0,
            "currency": "INR",
            "description": "Salary Payout - March",
            "timestamp": (base_time - timedelta(days=2)).isoformat(),
        },
        {
            "id": "tx_1003",
            "amount": 125000.0,
            "currency": "INR",
            "description": "Client Payment - Invoice INV-2025-001",
            "timestamp": (base_time - timedelta(days=1)).isoformat(),
        },
    ]

    return balance, transactions


def _mock_bank_two(token: str, simulate: SimulationMode) -> Tuple[float, List[Dict]]:
    """
    Simulate external BankTwo APIs for account summary and transaction history.
    """

    _simulate_failure(simulate)

    if not token or not token.endswith("_bank2"):
        raise BankingAPIError("INVALID_CREDENTIALS", "BankTwo token is invalid.")

    balance = 780_000.0
    base_time = datetime.utcnow()

    transactions = [
        {
            "id": "tx_2001",
            "amount": -22000.0,
            "currency": "INR",
            "description": "Cloud Hosting Charges",
            "timestamp": (base_time - timedelta(days=5)).isoformat(),
        },
        {
            "id": "tx_2002",
            "amount": -8500.0,
            "currency": "INR",
            "description": "Software Subscriptions",
            "timestamp": (base_time - timedelta(days=4)).isoformat(),
        },
        {
            "id": "tx_2003",
            "amount": 325000.0,
            "currency": "INR",
            "description": "Project Milestone Payment",
            "timestamp": (base_time - timedelta(days=2)).isoformat(),
        },
    ]

    return balance, transactions


def fetch_banking_data(
    provider: str,
    token: str,
    simulate: SimulationMode = None,
) -> Dict:
    """
    Unified entry point to fetch mock banking data from configured providers.

    Args:
        provider: Identifier of the banking provider ("bank1", "bank2").
        token: Mock auth token (patterns validated per provider).
        simulate: Optional simulation mode to force a specific failure.

    Returns:
        Dict with:
            - account_balance: float
            - transactions: List[Dict]
            - provider: str

    Raises:
        BankingAPIError: if the provider fails (timeout, invalid creds, etc.).
    """

    provider_lower = provider.lower()

    if provider_lower == "bank1":
        balance, txns = _mock_bank_one(token, simulate)
    elif provider_lower == "bank2":
        balance, txns = _mock_bank_two(token, simulate)
    else:
        raise BankingAPIError("UNSUPPORTED_PROVIDER", f"Unknown provider: {provider}")

    return {
        "provider": provider_lower,
        "account_balance": balance,
        "transactions": txns,
    }

