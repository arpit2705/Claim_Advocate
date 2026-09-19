"""
policy_extraction.py — Extracts structured Clause objects from a policy PDF.

Flow:
  1. pdfplumber reads the PDF page-by-page (page numbers are preserved).
  2. All text is passed through sanitizer.build_safe_prompt before any LLM call.
  3. Groq API returns JSON; Python validates and constructs Clause objects.
"""
from __future__ import annotations

import json
import uuid
from typing import Any

import pdfplumber
from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.extraction.sanitizer import build_safe_prompt
from app.schemas.policy import Clause

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

_EXTRACTION_INSTRUCTION = """
You are a policy analysis assistant. Extract ALL clauses from the insurance policy
document below. For each clause return a JSON object with exactly these fields:
  - clause_id: string (e.g. "CL-001", "CL-002", ...)
  - clause_type: one of ["exclusion", "sub_limit", "waiting_period", "condition", "coverage", "deadline"]
  - raw_text: the verbatim clause text
  - trigger_conditions: list of strings describing when this clause activates
  - page_number: integer page number where the clause appears (null if unknown)
  - day_count: integer — IF this clause states a simple day-based requirement (e.g. "within 30 days"), extract ONLY the plain integer day number.
  - day_count_context: string — the event the day count is measured from or to (e.g. "date of discharge").
  - deadline_rules: array of objects — IF the clause contains complex or multiple deadlines (e.g. intimation vs final submission, emergency vs planned). 
      Each object MUST have:
        - "event": "claim_intimation" or "final_claim_documents"
        - "hospitalization_type": "emergency", "planned", or null
        - "reference_event": "admission" or "discharge"
        - "deadline_value": integer
        - "deadline_unit": "hours" or "days"
      Return an empty array [] if not applicable.

Additionally, for waiting_period clauses only, also populate:
  - waiting_period_days: same integer as day_count
  - waiting_period_from: same string as day_count_context

Return exactly ONE JSON object matching the following structure:
{
  "clauses": [
    { ... clause object ... },
    { ... clause object ... }
  ]
}
Do not return an array at the root level. Do not return markdown. Do not return explanatory text.
""".strip()


def extract_text_from_pdf(pdf_path: str) -> dict[str, str]:
    """
    Reads a PDF and returns a dict mapping page labels to page text.
    Page labels are like "page_1", "page_2", etc.
    """
    pages: dict[str, str] = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            pages[f"page_{i}"] = text
    return pages


def _parse_clauses_from_json(raw_json: str, page_texts: dict[str, str]) -> list[Clause]:
    """
    Parses LLM JSON output into validated Clause objects.
    Assigns sequential IDs if the LLM omitted them. Validates clause_type.
    """
    import logging
    import re
    _log = logging.getLogger(__name__)

    valid_types = {"exclusion", "sub_limit", "waiting_period", "condition", "coverage", "deadline"}
    try:
        data: list[dict[str, Any]] = json.loads(raw_json)
    except json.JSONDecodeError:
        # Attempt to extract JSON array from surrounding text
        start = raw_json.find("[")
        end = raw_json.rfind("]") + 1
        if start != -1 and end > start:
            data = json.loads(raw_json[start:end])
        else:
            raise ValueError(f"Could not parse LLM JSON output: {raw_json[:200]}")

    clauses: list[Clause] = []
    for idx, item in enumerate(data):
        clause_type = item.get("clause_type", "condition")
        if clause_type not in valid_types:
            clause_type = "condition"

        clause_id = item.get("clause_id") or f"CL-{idx + 1:03d}"
        raw_text = item.get("raw_text", "").strip()
        if not raw_text:
            continue  # Skip empty clauses

        trigger_conditions = item.get("trigger_conditions", [])
        if not isinstance(trigger_conditions, list):
            trigger_conditions = [str(trigger_conditions)]

        page_number = item.get("page_number")
        if page_number is not None:
            try:
                page_number = int(page_number)
            except (ValueError, TypeError):
                page_number = None

        # ── Generic day_count: applies to ALL clause types ───────────────────
        day_count: int | None = None
        day_count_context: str | None = None

        # 1. Try structured field from LLM first
        raw_dc = item.get("day_count")
        if raw_dc is not None:
            try:
                dc = int(raw_dc)
                if dc > 0:
                    day_count = dc
                else:
                    _log.warning(f"[{clause_id}] day_count={raw_dc!r} is non-positive — treating as missing.")
            except (ValueError, TypeError):
                _log.warning(f"[{clause_id}] day_count={raw_dc!r} is not a clean integer — treating as missing.")

        raw_dcc = item.get("day_count_context")
        if isinstance(raw_dcc, str) and raw_dcc.strip():
            day_count_context = raw_dcc.strip()

        # 2. Regex fallback if LLM omitted day_count (handles "30 (thirty) days", "30 days")
        if day_count is None:
            m = re.search(r'\b(\d+)\s*(?:\([^)]+\))?\s*day', raw_text, re.IGNORECASE)
            if m:
                day_count = int(m.group(1))
                _log.info(f"[{clause_id}] day_count={day_count} extracted via regex fallback")

        # 3. Regex fallback for context if LLM omitted it
        if day_count_context is None and day_count is not None:
            # Try common "from/of/after <event>" patterns
            mc = re.search(
                r'(?:from|of|after)\s+(?:the\s+)?'
                r'(policy\s+inception\s+date|inception\s+date|commencement\s+date'
                r'|policy\s+start\s+date|date\s+of\s+discharge|discharge\s+date'
                r'|date\s+of\s+admission|admission\s+date'
                r'|date\s+of\s+diagnosis|first\s+diagnosis\s+date)',
                raw_text, re.IGNORECASE
            )
            if mc:
                day_count_context = mc.group(1).strip().lower()

        # ── waiting_period aliases (backward compat) ─────────────────────────
        waiting_period_days: int | None = None
        waiting_period_from: str | None = None
        if clause_type == "waiting_period":
            # Also check LLM's explicit waiting_period_days field (alias path)
            raw_wpd = item.get("waiting_period_days")
            if raw_wpd is not None and day_count is None:
                try:
                    wpd = int(raw_wpd)
                    if wpd > 0:
                        day_count = wpd
                except (ValueError, TypeError):
                    pass
            waiting_period_days = day_count
            waiting_period_from = day_count_context or item.get("waiting_period_from")

        clauses.append(
            Clause(
                clause_id=clause_id,
                clause_type=clause_type,
                raw_text=raw_text,
                trigger_conditions=trigger_conditions,
                page_number=page_number,
                day_count=day_count,
                day_count_context=day_count_context,
                waiting_period_days=waiting_period_days,
                waiting_period_from=waiting_period_from,
                deadline_rules=item.get("deadline_rules", []),
            )
        )
    return clauses

def extract_policy_metadata(pdf_path: str) -> dict[str, str | float | None]:
    """
    Deterministically extracts key numeric/date metadata from a policy PDF
    using regex on the raw text — NO LLM involved.

    Returns a dict with keys:
      - "sum_insured": float in rupees, or None if not found / not parseable
      - "policy_start_date": ISO 8601 string, or None
      - "policy_end_date": ISO 8601 string, or None
    """
    import re
    import logging
    _log = logging.getLogger(__name__)

    page_texts = extract_text_from_pdf(pdf_path)
    full_text = "\n".join(page_texts.values())

    result: dict[str, str | float | None] = {
        "sum_insured": None,
        "policy_start_date": None,
        "policy_end_date": None,
    }

    # ── Sum Insured ─────────────────────────────────────────────────────────
    _SI_PATTERNS = [
        re.compile(
            r"(?:sum\s+insured|sum\s+assured)\s*[:\-]?\s*(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d{1,2})?)",
            re.IGNORECASE,
        ),
        re.compile(
            r"(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d{1,2})?)\s*/?\s*-?\s*(?:sum\s+insured|sum\s+assured)",
            re.IGNORECASE,
        ),
    ]
    for pat in _SI_PATTERNS:
        m = pat.search(full_text)
        if m:
            raw_num = m.group(1).replace(",", "")
            try:
                result["sum_insured"] = float(raw_num)
                break
            except ValueError:
                pass

    # ── Policy Period Dates ─────────────────────────────────────────────────
    # We support multiple date formats in the source PDF:
    #   DD/MM/YYYY  DD-MM-YYYY  YYYY-MM-DD  DD Mon YYYY  Mon DD, YYYY

    _MONTH_MAP = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04",
        "may": "05", "jun": "06", "jul": "07", "aug": "08",
        "sep": "09", "oct": "10", "nov": "11", "dec": "12",
    }

    def _any_date_to_iso(raw: str) -> str | None:
        """Try every known format; return ISO string or None."""
        raw = raw.strip()
        # YYYY-MM-DD (already ISO)
        m = re.match(r"^(\d{4})[/\-](\d{2})[/\-](\d{2})$", raw)
        if m:
            return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
        # DD/MM/YYYY or DD-MM-YYYY
        m = re.match(r"^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$", raw)
        if m:
            return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
        # DD Mon YYYY
        m = re.match(r"^(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})$", raw)
        if m:
            mon = m.group(2).lower()[:3]
            if mon in _MONTH_MAP:
                return f"{m.group(3)}-{_MONTH_MAP[mon]}-{m.group(1).zfill(2)}"
        # Mon DD, YYYY
        m = re.match(r"^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$", raw)
        if m:
            mon = m.group(1).lower()[:3]
            if mon in _MONTH_MAP:
                return f"{m.group(3)}-{_MONTH_MAP[mon]}-{m.group(2).zfill(2)}"
        return None

    # Generic date token pattern — matches all the formats above
    _DT_TOKEN = (
        r"(?:"
        r"\d{4}[/\-]\d{2}[/\-]\d{2}"           # YYYY-MM-DD
        r"|\d{1,2}[/\-]\d{1,2}[/\-]\d{4}"       # DD/MM/YYYY or DD-MM-YYYY
        r"|\d{1,2}\s+[A-Za-z]+\s+\d{4}"         # DD Mon YYYY
        r"|[A-Za-z]+\s+\d{1,2},?\s+\d{4}"       # Mon DD, YYYY
        r")"
    )

    # Strategy 1: labeled period block  e.g. "Policy Period: 01-03-2025 to 28-02-2026"
    _PERIOD_RE = re.compile(
        r"(?:policy\s+period|period\s+of\s+insurance|cover\s+(?:period|from)|policy\s+term)"
        r"[\s:\-]*(" + _DT_TOKEN + r")"
        r"[\s\-–toTO]*"
        r"(" + _DT_TOKEN + r")",
        re.IGNORECASE,
    )
    pm = _PERIOD_RE.search(full_text)
    if pm:
        result["policy_start_date"] = _any_date_to_iso(pm.group(1))
        result["policy_end_date"] = _any_date_to_iso(pm.group(2))

    # Strategy 2: labeled inception/expiry on separate lines
    if result["policy_start_date"] is None:
        _INCEP_RE = re.compile(
            r"(?:inception\s+date|commencement\s+date|start\s+date|effective\s+date|from\s+date)"
            r"[\s:\-]*(" + _DT_TOKEN + r")",
            re.IGNORECASE,
        )
        m = _INCEP_RE.search(full_text)
        if m:
            result["policy_start_date"] = _any_date_to_iso(m.group(1))

    if result["policy_end_date"] is None:
        _EXPIRY_RE = re.compile(
            r"(?:expiry\s+date|expiration\s+date|end\s+date|to\s+date|valid\s+(?:up\s+)?to)"
            r"[\s:\-]*(" + _DT_TOKEN + r")",
            re.IGNORECASE,
        )
        m = _EXPIRY_RE.search(full_text)
        if m:
            result["policy_end_date"] = _any_date_to_iso(m.group(1))

    # Strategy 3: last-resort — first two DD-MM-YYYY or YYYY-MM-DD dates in doc
    # (only if BOTH are still missing — avoids partial contamination)
    if result["policy_start_date"] is None and result["policy_end_date"] is None:
        _FALLBACK_DATE_RE = re.compile(
            r"(\d{1,2}[/\-]\d{1,2}[/\-]\d{4}|\d{4}[/\-]\d{2}[/\-]\d{2})"
        )
        all_dates = _FALLBACK_DATE_RE.findall(full_text)
        if len(all_dates) >= 2:
            result["policy_start_date"] = _any_date_to_iso(all_dates[0])
            result["policy_end_date"] = _any_date_to_iso(all_dates[1])
            _log.warning(
                f"[POLICY META] Used last-resort date fallback: "
                f"start={result['policy_start_date']}, end={result['policy_end_date']}. "
                f"Labeled period/inception patterns did not match."
            )

    # ── STEP 1 DIAGNOSTIC: point (a) ────────────────────────────────────────
    _log.info(
        f"[POLICY META DIAG (a)] Extracted from policy PDF: "
        f"sum_insured={result['sum_insured']}, "
        f"policy_start_date='{result['policy_start_date']}', "
        f"policy_end_date='{result['policy_end_date']}'"
    )

    return result




def extract_clauses_from_pdf(pdf_path: str) -> list[Clause]:
    """
    Main entry point: reads a policy PDF and returns a list of Clause objects.

    Parameters
    ----------
    pdf_path : str
        Absolute or relative path to the policy PDF file.

    Returns
    -------
    list[Clause]
        Validated and structured clause list.

    Raises
    ------
    RuntimeError
        If GROQ_API_KEY is not configured.
    """
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set. Cannot call LLM.")

    page_texts = extract_text_from_pdf(pdf_path)
    # Combine all pages into a single document block; label carries page info
    full_text = "\n\n".join(
        f"[Page {label.split('_')[1]}]\n{text}"
        for label, text in page_texts.items()
        if text.strip()
    )

    system_prompt, user_prompt = build_safe_prompt(
        task_instruction=_EXTRACTION_INSTRUCTION,
        documents={"policy_pdf": full_text},
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

    raw_json = response.choices[0].message.content or "[]"
    # Groq json_object mode wraps in an object; unwrap if needed
    try:
        parsed = json.loads(raw_json)
        if isinstance(parsed, dict):
            # Find the first list value
            for v in parsed.values():
                if isinstance(v, list):
                    raw_json = json.dumps(v)
                    break
    except json.JSONDecodeError:
        pass

    return _parse_clauses_from_json(raw_json, page_texts)


def extract_clauses_from_text(policy_text: str) -> list[Clause]:
    """
    Extracts clauses from raw policy text (no PDF needed).
    Useful for unit tests or when text is already extracted.
    """
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set. Cannot call LLM.")

    system_prompt, user_prompt = build_safe_prompt(
        task_instruction=_EXTRACTION_INSTRUCTION,
        documents={"policy_text": policy_text},
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

    raw_json = response.choices[0].message.content or "[]"
    try:
        parsed = json.loads(raw_json)
        if isinstance(parsed, dict):
            for v in parsed.values():
                if isinstance(v, list):
                    raw_json = json.dumps(v)
                    break
    except json.JSONDecodeError:
        pass

    return _parse_clauses_from_json(raw_json, {})
