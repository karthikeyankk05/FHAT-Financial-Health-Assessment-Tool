"""
PDF parsing utilities for extracting high-level financial fields
from text-based PDF statements.

This module is intentionally conservative – it looks for simple
`key: value` or `key value` patterns in the extracted text.

Requires:
    pip install pdfplumber
"""

from typing import Dict
import re

import pdfplumber  # type: ignore[import]
from fastapi import UploadFile


FINANCIAL_FIELDS = [
    "revenue",
    "expenses",
    "assets",
    "liabilities",
    "inventory",
]


class PDFParsingError(Exception):
    """Raised when a PDF cannot be parsed into the expected structure."""


def _extract_text_from_pdf(upload_file: UploadFile) -> str:
    """
    Extract raw text from a text-based PDF using pdfplumber.

    Raises:
        PDFParsingError: if the PDF cannot be read.
    """

    try:
        # Reset file pointer in case it has been read elsewhere
        upload_file.file.seek(0)

        text_chunks = []
        with pdfplumber.open(upload_file.file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_chunks.append(page_text)

        full_text = "\n".join(text_chunks).strip()
        if not full_text:
            raise PDFParsingError("No extractable text found in PDF.")

        return full_text

    except Exception as exc:  # pragma: no cover - defensive
        raise PDFParsingError(f"Failed to read PDF: {exc}") from exc


def _parse_numeric(value_str: str) -> float:
    """
    Parse a numeric string that may contain commas, currency symbols, or spaces.
    """

    cleaned = re.sub(r"[^\d.\-]", "", value_str)
    if cleaned in ("", "-", ".", "-."):
        raise ValueError(f"Could not parse numeric value from: {value_str!r}")
    return float(cleaned)


def parse_financial_fields_from_text(text: str) -> Dict[str, float]:
    """
    Parse core financial fields from raw PDF text.

    Expected patterns per field (case-insensitive):
        - 'Revenue: 123,456'
        - 'revenue 123456'
        - 'Total Revenue - 123456'

    Returns:
        Dict[str, float]: mapping of financial field -> numeric value.

    Raises:
        PDFParsingError: if required fields are missing.
    """

    lower_text = text.lower()

    results: Dict[str, float] = {}
    for field in FINANCIAL_FIELDS:
        # Build a flexible regex pattern for each key
        # Example: r"revenue\s*[:\-]?\s*([0-9,.\s]+)"
        pattern = rf"{field}\s*[:\-]?\s*([0-9,.\s]+)"
        match = re.search(pattern, lower_text, flags=re.IGNORECASE)

        if not match:
            continue

        raw_value = match.group(1)
        try:
            results[field] = _parse_numeric(raw_value)
        except ValueError:
            # Skip malformed numeric values – caller will treat as missing
            continue

    missing = [f for f in FINANCIAL_FIELDS if f not in results]
    if missing:
        raise PDFParsingError(f"Missing required fields in PDF text: {missing}")

    return results


def parse_pdf_financials(upload_file: UploadFile) -> Dict[str, float]:
    """
    High-level helper used by routes to go from an uploaded PDF file
    to a structured dict of financial metrics.

    Returns:
        Dict[str, float]: mapping of
            revenue, expenses, assets, liabilities, inventory

    Raises:
        PDFParsingError: for any parsing-related issue.
    """

    text = _extract_text_from_pdf(upload_file)
    return parse_financial_fields_from_text(text)

