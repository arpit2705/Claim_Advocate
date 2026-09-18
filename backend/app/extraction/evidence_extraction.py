"""
evidence_extraction.py — Extracts structured EvidenceFact objects from claim
documents (hospital bills, discharge summaries, rejection letters, etc.).

Key responsibility: NORMALIZE all dates to ISO 8601 (YYYY-MM-DD) and all
monetary amounts to plain numeric strings (no currency symbols) — done in
Python after the LLM returns raw values, not left to the LLM alone.

Flow:
  1. pdfplumber reads PDFs page-by-page.
  2. Text is wrapped via sanitizer.build_safe_prompt before any LLM call.
  3. Groq returns JSON facts; Python normalizes dates/amounts and validates.
"""
from __future__ import annotations

import json
import re
import uuid
from typing import Any

import pdfplumber
from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.extraction.sanitizer import build_safe_prompt
from app.schemas.evidence import EvidenceFact

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

_EXTRACTION_INSTRUCTION = """
You are a claim document analysis assistant. Extract ALL factual fields from the
documents below. For each fact return a JSON object with exactly these fields:
  - fact_id: string (e.g. "F-001", "F-002", ...)
  - field: the name of the fact field (e.g. "admission_date", "discharge_date",
           "claim_amount", "patient_name", "hospital_name", "diagnosis", "policy_number")
  - value: the raw value as it appears in the document
  - source_document: the document label provided
  - page: integer page number where found (null if unknown)
  - confidence: float 0.0–1.0 reflecting how clearly this fact appears

Return a JSON array of fact objects. No prose outside the JSON.
""".strip()

# ── Date normalization ────────────────────────────────────────────────────────

_MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}

_DATE_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Already ISO: 2024-03-15
    (re.compile(r"^(\d{4})-(\d{2})-(\d{2})$"), "iso"),
    # DD/MM/YYYY or DD-MM-YYYY
    (re.compile(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$"), "dmy"),
    # MM/DD/YYYY
    (re.compile(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$"), "mdy"),
    # DD Mon YYYY  e.g. "15 March 2024"
    (re.compile(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$"), "dmonthy"),
    # Mon DD, YYYY  e.g. "March 15, 2024"
    (re.compile(r"^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$"), "monthy"),
]


def normalize_date(value: str) -> str:
    """
    Attempts to convert a date string to ISO 8601 (YYYY-MM-DD).
    Returns the original string unchanged if no pattern matches.
    """
    v = value.strip()

    # Already ISO
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", v)
    if m:
        return v

    # DD/MM/YYYY or DD-MM-YYYY
    m = re.match(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$", v)
    if m:
        d, mo, y = m.group(1), m.group(2), m.group(3)
        return f"{y}-{mo.zfill(2)}-{d.zfill(2)}"

    # DD Mon YYYY
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", v)
    if m:
        d, mon, y = m.group(1), m.group(2).lower()[:3], m.group(3)
        if mon in _MONTH_MAP:
            return f"{y}-{_MONTH_MAP[mon]}-{d.zfill(2)}"

    # Mon DD, YYYY
    m = re.match(r"^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$", v)
    if m:
        mon, d, y = m.group(1).lower()[:3], m.group(2), m.group(3)
        if mon in _MONTH_MAP:
            return f"{y}-{_MONTH_MAP[mon]}-{d.zfill(2)}"

    return v  # Return unchanged if no pattern matched


# ── Amount normalization ──────────────────────────────────────────────────────

_AMOUNT_RE = re.compile(
    r"[₹$€£¥]?\s*([\d,]+(?:\.\d{1,2})?)\s*(?:INR|USD|EUR|GBP)?", re.IGNORECASE
)

_DATE_FIELDS = {
    "admission_date", "discharge_date", "claim_date", "incident_date",
    "treatment_date", "surgery_date", "policy_start_date", "policy_end_date",
    "date_of_birth", "dob", "date", "from_date", "to_date",
}
_AMOUNT_FIELDS = {
    "claim_amount", "approved_amount", "billed_amount", "paid_amount",
    "deductible", "copay", "premium", "sub_limit_amount", "amount",
    "total_amount", "net_amount",
}


def normalize_value(field: str, value: str) -> str:
    """
    Normalizes a fact value based on its field name:
    - Date fields → ISO 8601
    - Amount fields → plain numeric string without currency symbols
    - Other fields → stripped as-is
    """
    field_lower = field.lower()
    v = value.strip()

    if any(kw in field_lower for kw in _DATE_FIELDS):
        return normalize_date(v)

    if any(kw in field_lower for kw in _AMOUNT_FIELDS):
        m = _AMOUNT_RE.search(v)
        if m:
            return m.group(1).replace(",", "")
        return v

    return v


# ── PDF reading ───────────────────────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> dict[str, str]:
    """Reads a PDF and returns {page_label: page_text} mapping."""
    pages: dict[str, str] = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages[f"page_{i}"] = text
    return pages


# ── LLM + validation ─────────────────────────────────────────────────────────

def _call_llm(documents: dict[str, str]) -> list[dict[str, Any]]:
    """Calls Groq LLM and returns raw parsed JSON list of fact dicts."""
    system_prompt, user_prompt = build_safe_prompt(
        task_instruction=_EXTRACTION_INSTRUCTION,
        documents=documents,
    )
    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "[]"
    parsed = json.loads(raw)
    if isinstance(parsed, dict):
        for v in parsed.values():
            if isinstance(v, list):
                return v
        return []
    if isinstance(parsed, list):
        return parsed
    return []


def _build_facts(raw_facts: list[dict[str, Any]], source_label: str) -> list[EvidenceFact]:
    """Validates and normalizes raw LLM fact dicts into EvidenceFact objects."""
    facts: list[EvidenceFact] = []
    for idx, item in enumerate(raw_facts):
        field = str(item.get("field", "unknown")).strip()
        raw_value = str(item.get("value", "")).strip()
        value = normalize_value(field, raw_value)

        fact_id = item.get("fact_id") or f"F-{idx + 1:03d}"
        source_document = item.get("source_document") or source_label

        page = item.get("page")
        if page is not None:
            try:
                page = int(page)
            except (ValueError, TypeError):
                page = None

        confidence = float(item.get("confidence", 0.8))
        confidence = max(0.0, min(1.0, confidence))

        facts.append(
            EvidenceFact(
                fact_id=fact_id,
                field=field,
                value=value,
                source_document=source_document,
                page=page,
                confidence=confidence,
            )
        )
    return facts


# ── Public API ────────────────────────────────────────────────────────────────

def extract_facts_from_pdf(pdf_path: str, document_label: str | None = None) -> list[EvidenceFact]:
    """
    Extracts EvidenceFact objects from a claim document PDF.

    Parameters
    ----------
    pdf_path : str
        Path to the PDF file.
    document_label : str | None
        Human-readable label for this document (e.g. "hospital_bill").
        Defaults to the filename.

    Returns
    -------
    list[EvidenceFact]
        Normalized and validated facts.
    """
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set.")

    import os
    label = document_label or os.path.basename(pdf_path)
    page_texts = extract_text_from_pdf(pdf_path)
    full_text = "\n\n".join(
        f"[Page {k.split('_')[1]}]\n{v}" for k, v in page_texts.items() if v.strip()
    )
    raw_facts = _call_llm({label: full_text})
    return _build_facts(raw_facts, label)


def extract_facts_from_text(
    text: str, document_label: str = "document"
) -> list[EvidenceFact]:
    """
    Extracts EvidenceFact objects from raw text (no PDF needed).
    Useful for tests or when text is already extracted.
    """
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set.")

    raw_facts = _call_llm({document_label: text})
    return _build_facts(raw_facts, document_label)


def extract_facts_from_texts(
    documents: dict[str, str]
) -> list[EvidenceFact]:
    """
    Extracts EvidenceFact objects from multiple named text blocks in one LLM call.

    Parameters
    ----------
    documents : dict[str, str]
        Mapping of document_label -> text.

    Returns
    -------
    list[EvidenceFact]
        Combined normalized facts from all documents.
    """
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set.")

    raw_facts = _call_llm(documents)
    return _build_facts(raw_facts, "multi_document")
