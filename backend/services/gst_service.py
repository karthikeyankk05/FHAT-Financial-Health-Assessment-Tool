"""
GST filing import and validation utilities.

Supports ingestion from JSON and CSV files and produces a normalized
GST payload with the following fields:
    - gst_collected
    - gst_paid
    - input_credit
    - output_tax
"""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from typing import Dict, BinaryIO


GST_FIELDS = ["gst_collected", "gst_paid", "input_credit", "output_tax"]


@dataclass
class GSTParsingError(Exception):
    """Raised when GST data cannot be parsed from the source file."""

    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


@dataclass
class GSTValidationError(Exception):
    """Raised when GST data fails internal consistency checks."""

    message: str

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.message


def _to_float(value) -> float:
    try:
        return float(value)
    except Exception as exc:
        raise GSTParsingError(f"Invalid numeric value: {value!r}") from exc


def parse_gst_from_json_bytes(raw_bytes: bytes) -> Dict[str, float]:
    """
    Parse GST metrics from a JSON payload.

    Expected shape (keys may be strings or numbers):
    {
        "gst_collected": ...,
        "gst_paid": ...,
        "input_credit": ...,
        "output_tax": ...
    }
    """

    try:
        data = json.loads(raw_bytes.decode("utf-8"))
    except Exception as exc:
        raise GSTParsingError(f"Invalid JSON: {exc}") from exc

    result: Dict[str, float] = {}
    for field in GST_FIELDS:
        if field not in data:
            raise GSTParsingError(f"Missing field in JSON: {field}")
        result[field] = _to_float(data[field])

    return result


def parse_gst_from_csv_file(file_obj: BinaryIO) -> Dict[str, float]:
    """
    Parse GST metrics from a CSV payload.

    Expected header columns include GST_FIELDS; only the first row is used.
    """

    try:
        file_obj.seek(0)
        text_stream = io.TextIOWrapper(file_obj, encoding="utf-8")
        reader = csv.DictReader(text_stream)
        first_row = next(reader, None)
    except Exception as exc:
        raise GSTParsingError(f"Invalid CSV: {exc}") from exc

    if not first_row:
        raise GSTParsingError("CSV contained no rows.")

    result: Dict[str, float] = {}
    for field in GST_FIELDS:
        if field not in first_row:
            raise GSTParsingError(f"Missing column in CSV: {field}")
        result[field] = _to_float(first_row[field])

    return result


def validate_gst_consistency(gst_data: Dict[str, float]) -> None:
    """
    Perform simple internal consistency checks on GST data.

    Rules (very high-level heuristics for MVP):
        - gst_collected should roughly equal output_tax (+/- 10%)
        - gst_collected should be >= gst_paid (otherwise high refund scenario)
    """

    gst_collected = gst_data["gst_collected"]
    gst_paid = gst_data["gst_paid"]
    input_credit = gst_data["input_credit"]
    output_tax = gst_data["output_tax"]

    # 1. Output tax vs collected
    if output_tax <= 0 or gst_collected <= 0:
        raise GSTValidationError("GST collected and output tax must both be positive.")

    ratio = gst_collected / output_tax
    if ratio < 0.9 or ratio > 1.1:
        raise GSTValidationError(
            f"GST collected ({gst_collected}) does not align with output tax ({output_tax})."
        )

    # 2. Basic reasonability: collected vs paid vs credit
    if gst_paid > (gst_collected + input_credit) * 1.2:
        raise GSTValidationError("GST paid appears unusually high relative to collected and credit.")

