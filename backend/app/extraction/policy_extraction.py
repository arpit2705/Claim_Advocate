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
  - clause_type: one of ["exclusion", "sub_limit", "waiting_period", "condition", "coverage"]
  - raw_text: the verbatim clause text
  - trigger_conditions: list of strings describing when this clause activates
  - page_number: integer page number where the clause appears (null if unknown)

Return a JSON array of clause objects. No prose outside the JSON.
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
    valid_types = {"exclusion", "sub_limit", "waiting_period", "condition", "coverage"}
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

        clauses.append(
            Clause(
                clause_id=clause_id,
                clause_type=clause_type,
                raw_text=raw_text,
                trigger_conditions=trigger_conditions,
                page_number=page_number,
            )
        )
    return clauses


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
