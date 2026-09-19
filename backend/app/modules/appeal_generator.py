"""
appeal_generator.py — Grounded-only appeal letter generation.

HARD RULE: If grounded=False, this module MUST return None and refuse to draft
an appeal letter. An appeal letter is only generated when:
  1. grounded=True (clauses + facts are verified present)
  2. verdict is "likely_misapplied" or "questionable"

All document-derived text passes through sanitizer.build_safe_prompt.
Every clause_id cited in the appeal letter must exist in the provided clause list —
enforced by Python post-generation citation scan.
"""
from __future__ import annotations

import json
import re

from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.extraction.sanitizer import build_safe_prompt
from app.schemas.evidence import EvidenceFact
from app.schemas.policy import Clause
from app.schemas.verdict import Verdict

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

_APPEAL_INSTRUCTION = """
You are an insurance claim advocate drafting a formal appeal letter on behalf of a
policyholder whose claim was rejected.

Write a formal, factual appeal letter that:
  1. Cites the EXACT clause text from the policy documents provided (use clause IDs)
  2. References specific claim facts from the submitted evidence
  3. Explains specifically why the rejection reason does not apply given the clause
     language and facts
  4. Uses professional, neutral language
  5. Does NOT speculate beyond what the documents state
  6. Does NOT make up clause IDs or facts not present in the data below

Return a JSON object with one key: "appeal_letter" (string containing the full letter).
""".strip()

# Matches clause IDs like CL-001, Clause 4.2, Section 4.2(b)
_CLAUSE_ID_RE = re.compile(r"\b(?:CL-\d+|Clause\s+[\d.a-zA-Z()]+|Section\s+[\d.a-zA-Z()]+)\b", re.IGNORECASE)

def _extract_cited_clause_ids(text: str) -> set[str]:
    """Extracts all clause_id references from generated text."""
    return set(_CLAUSE_ID_RE.findall(text))


def generate_appeal(
    verdict: Verdict,
    clauses: list[Clause],
    facts: list[EvidenceFact],
    rejection_reason: str,
    grounded: bool,
) -> str | None:
    """
    Generates a grounded appeal letter, or returns None if not warranted.

    Parameters
    ----------
    verdict : Verdict
        The final validated verdict.
    clauses : list[Clause]
        Retrieved policy clauses (only verified clause_ids will be cited).
    facts : list[EvidenceFact]
        Extracted claim facts.
    rejection_reason : str
        The insurer's stated rejection reason.
    grounded : bool
        Whether the result is grounded in verified clauses and facts.
        MUST be True to generate an appeal — returns None if False.

    Returns
    -------
    str | None
        The appeal letter text, or None if grounded=False or verdict doesn't
        warrant an appeal.
    """
    # Hard rule: refuse if not grounded
    if not grounded:
        return None

    # Only draft appeal for misapplied or questionable verdicts
    if verdict.verdict not in {"likely_misapplied", "questionable"}:
        return None

    if _client is None:
        return None

    known_clause_ids = {c.clause_id for c in clauses}

    clause_text = "\n\n".join(
        f"[{c.clause_id}] ({c.clause_type}):\n{c.raw_text}"
        for c in clauses
    )
    fact_text = "\n".join(
        f"- {f.field}: {f.value} (source: {f.source_document}, page: {f.page})"
        for f in facts
    )
    context = (
        f"INSURER REJECTION REASON:\n{rejection_reason}\n\n"
        f"ADJUDICATION VERDICT: {verdict.verdict}\n"
        f"VERDICT EXPLANATION: {verdict.mismatch_explanation}\n\n"
        f"POLICY CLAUSES:\n{clause_text}\n\n"
        f"CLAIM FACTS:\n{fact_text}"
    )

    system_prompt, user_prompt = build_safe_prompt(
        task_instruction=_APPEAL_INSTRUCTION,
        documents={"appeal_context": context},
    )

    import logging
    _log = logging.getLogger(__name__)

    for attempt in range(2):
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        try:
            parsed = json.loads(raw)
            letter = parsed.get("appeal_letter", "")
            if letter:
                break
        except json.JSONDecodeError:
            _log.warning("Appeal generation JSON parse failed (attempt %d). Raw output: %s", attempt + 1, raw)
            continue
    else:
        return "Error: Appeal generation failed, please retry."

    # Python citation validation: remove any hallucinated clause IDs
    cited_ids = _extract_cited_clause_ids(letter)
    hallucinated = cited_ids - known_clause_ids
    if hallucinated:
        for bad_id in hallucinated:
            letter = letter.replace(bad_id, f"[CITATION_NOT_VERIFIED:{bad_id}]")

    return letter
