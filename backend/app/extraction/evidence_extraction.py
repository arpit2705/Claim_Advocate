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
You are a claim document analysis assistant. Analyze the provided CLAIM DOCUMENT.

Step 1: Classify the document.
Determine its type from this exact list: claim_form, discharge_summary, hospital_bill, payment_receipt, prescription, investigation_report, identity_proof, other.
Also provide a confidence score (0.0 to 1.0).

Step 2: Extract factual fields.
Extract facts into a flat object. Use null for unavailable fields. Do not fabricate values.
Expected fields:
  - policy_number: string
  - patient_name: string
  - claimant_name: string
  - admission_date: string (YYYY-MM-DD)
  - discharge_date: string (YYYY-MM-DD)
  - hospital_name: string (core hospital name only)
  - hospital_department: string
  - doctor_name: string
  - doctor_qualifications: array of strings
  - core_illness: string
  - illness_modifiers: array of strings
  - medical_procedure: string
  - billing_items: array of strings
  - claim_amount: number
  - room_rent_per_day: number
  - room_rent_quantity_days: integer
  - room_rent_total: number
  - claim_intimation_date: string (YYYY-MM-DD or YYYY-MM-DDTHH:MM)
  - claim_submission_date: string (YYYY-MM-DD)
  - notification_delay_hours: integer (extract if stated explicitly, e.g., 'notified X hours after admission')
  - treatment_type: string (e.g., 'emergency', 'planned')

Return exactly ONE JSON object matching this structure:
{
  "document_classification": {
    "document_type": "...",
    "confidence": 0.95
  },
  "facts": {
    "policy_number": null,
    "patient_name": "...",
    ...
  }
}
Do not return an array at the root level. Do not return markdown. Do not return explanatory text.
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
    "date_of_birth", "dob", "date", "from_date", "to_date", "claim_submission_date"
}
_AMOUNT_FIELDS = {
    "claim_amount", "room_rent_per_day", "room_rent_total", "approved_amount", "billed_amount", "paid_amount",
    "deductible", "copay", "premium", "sub_limit_amount", "amount",
    "total_amount", "net_amount", "sum_insured"
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

def _call_llm(documents: dict[str, str]) -> dict[str, Any]:
    """Calls Groq LLM and returns raw parsed JSON dict for the document."""
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
    raw = response.choices[0].message.content or "{}"
    
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("Evidence extraction failed: LLM returned invalid JSON.")
        
    if not isinstance(parsed, dict):
        raise ValueError(f"Evidence extraction failed: Expected JSON object, received {type(parsed).__name__}.")
        
    return parsed


_POLICY_ONLY_FIELDS = {"sum_insured", "policy_start_date", "policy_end_date"}

from app.extraction.field_normalization import normalize_field_name

def _build_facts(raw_obj: dict[str, Any], source_label: str) -> tuple[str, list[EvidenceFact]]:
    """Validates and normalizes raw LLM output into (document_type, list[EvidenceFact])."""
    import logging
    _log = logging.getLogger(__name__)
    facts: list[EvidenceFact] = []
    
    classification = raw_obj.get("document_classification", {})
    doc_type = classification.get("document_type", "other")
    
    raw_facts = raw_obj.get("facts", {})
    if not isinstance(raw_facts, dict):
        raw_facts = {}

    idx = 1
    for raw_field, raw_value in raw_facts.items():
        if raw_value is None or str(raw_value).strip() == "":
            continue
            
        field = normalize_field_name(raw_field)
        raw_value_str = str(raw_value).strip()

        # STEP 2: Drop policy-only fields that LLM may mistakenly extract from claim docs
        if field.lower() in _POLICY_ONLY_FIELDS:
            _log.warning(
                f"Dropping field '{field}' from claim extraction — this is a policy-only field "
                f"(source: {source_label}). Raw value was: '{raw_value_str}'"
            )
            continue

        value = normalize_value(field, raw_value_str)

        # STEP 3: Numeric validation gate — reject non-numeric values for amount fields
        if field.lower() in _AMOUNT_FIELDS:
            # After normalization, value must be a clean number string
            try:
                float(value.replace(",", ""))
            except (ValueError, AttributeError):
                _log.warning(
                    f"Dropping non-numeric amount field '{field}' = '{raw_value_str}' "
                    f"(normalized to '{value}') from {source_label} — not a usable number."
                )
                continue

        fact_id = f"F-{idx:03d}"
        idx += 1
        
        # We always use the assigned document type for the source_document
        source_document = doc_type

        # We assume high confidence for now as Groq doesn't provide per-field confidence in this schema
        confidence = 0.9

        facts.append(
            EvidenceFact(
                fact_id=fact_id,
                field=field,
                value=value,
                source_document=source_document,
                page=None,
                confidence=confidence,
            )
        )
    return doc_type, facts


# ── Public API ───────────────────────────────────────────────────────────────

def extract_facts_from_pdf(pdf_path: str, document_label: str | None = None) -> tuple[str, list[EvidenceFact]]:
    """
    Extracts document type and EvidenceFact objects from a claim document PDF.

    Parameters
    ----------
    pdf_path : str
        Path to the PDF file.
    document_label : str | None
        Human-readable label for this document (e.g. "hospital_bill").
        Defaults to the filename.

    Returns
    -------
    tuple[str, list[EvidenceFact]]
        (document_type, list of normalized facts).
    """
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set.")

    import os
    label = document_label or os.path.basename(pdf_path)
    page_texts = extract_text_from_pdf(pdf_path)
    full_text = "\n\n".join(
        f"[Page {k.split('_')[1]}]\n{v}" for k, v in page_texts.items() if v.strip()
    )
    if not full_text.strip():
        raise ValueError("PDF text extraction returned empty content (possibly an image-only PDF requiring OCR or an invalid file).")
    raw_obj = _call_llm({label: full_text})
    return _build_facts(raw_obj, label)


def extract_facts_from_text(
    text: str, document_label: str = "document"
) -> tuple[str, list[EvidenceFact]]:
    """
    Extracts EvidenceFact objects from raw text (no PDF needed).
    Useful for tests or when text is already extracted.
    """
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set.")

    raw_obj = _call_llm({document_label: text})
    return _build_facts(raw_obj, document_label)


def extract_facts_from_texts(
    documents: dict[str, str]
) -> tuple[str, list[EvidenceFact]]:
    """
    Extracts EvidenceFact objects from multiple named text blocks in one LLM call.
    Note: For true multi-document handling, this should ideally be called per document.
    """
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set.")

    raw_obj = _call_llm(documents)
    return _build_facts(raw_obj, "multi_document")
