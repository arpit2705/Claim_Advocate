"""
policy_evidence_reasoner.py — LLM adjudication reasoning with 3-pass self-consistency.

Flow per call:
  1. Retrieve the most relevant clause(s) for the rejection reason.
  2. Run 3 independent LLM reasoning passes (different seeds via temperature jitter).
  3. Each pass returns a structured verdict + explanation.
  4. consistency.py tallies the agreement across passes → consistency_score.

The LLM proposes a verdict. Python (decision_validator.py) has final say.
"""
from __future__ import annotations

import json
from typing import Any

from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.extraction.sanitizer import build_safe_prompt
from app.schemas.evidence import EvidenceFact
from app.schemas.policy import Clause

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

_VALID_VERDICTS = {"valid", "questionable", "likely_misapplied", "insufficient_evidence"}

_REASONING_INSTRUCTION = """
You are an insurance claim adjudication assistant. You will be given:
  - A rejection reason stated by the insurer
  - The policy clause(s) cited or retrieved
  - The claim facts extracted from submitted documents

Your task: determine whether the insurer's rejection reason is supported by the
policy clause and the claim facts.

Return a JSON object with exactly these fields:
  - verdict: one of ["valid", "questionable", "likely_misapplied", "insufficient_evidence"]
    * "valid": the rejection is clearly supported by the clause and facts
    * "questionable": the rejection has some basis but the application is unclear
    * "likely_misapplied": the clause does not clearly support the rejection
    * "insufficient_evidence": facts are too incomplete to determine either way
  - explanation: 2-4 sentence reasoning citing specific clause language and facts
  - matched_clause_id: the clause_id most relevant to this rejection (or null)
  - mismatch_explanation: if verdict is not "valid", explain the specific mismatch

Return only the JSON object. No prose outside it.
""".strip()


def _single_pass(
    rejection_reason: str,
    clauses: list[Clause],
    facts: list[EvidenceFact],
    temperature: float,
) -> dict[str, Any]:
    """Runs one LLM reasoning pass and returns the parsed JSON dict."""
    clause_text = "\n\n".join(
        f"[{c.clause_id}] ({c.clause_type}): {c.raw_text}" for c in clauses
    )
    fact_text = "\n".join(
        f"- {f.field}: {f.value} (source: {f.source_document}, confidence: {f.confidence:.2f})"
        for f in facts
    )
    context = (
        f"REJECTION REASON:\n{rejection_reason}\n\n"
        f"RELEVANT POLICY CLAUSES:\n{clause_text}\n\n"
        f"CLAIM FACTS:\n{fact_text}"
    )

    system_prompt, user_prompt = build_safe_prompt(
        task_instruction=_REASONING_INSTRUCTION,
        documents={"adjudication_context": context},
    )

    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content or "{}"
    parsed = json.loads(raw)

    # Normalise verdict
    verdict = parsed.get("verdict", "insufficient_evidence")
    if verdict not in _VALID_VERDICTS:
        verdict = "insufficient_evidence"
    parsed["verdict"] = verdict
    parsed.setdefault("explanation", "")
    parsed.setdefault("matched_clause_id", None)
    parsed.setdefault("mismatch_explanation", "")
    return parsed


def run_three_pass_reasoning(
    rejection_reason: str,
    clauses: list[Clause],
    facts: list[EvidenceFact],
) -> list[dict[str, Any]]:
    """
    Runs 3 independent LLM reasoning passes and returns all three result dicts.

    Parameters
    ----------
    rejection_reason : str
        The insurer's stated reason for rejection.
    clauses : list[Clause]
        Retrieved policy clauses relevant to the rejection.
    facts : list[EvidenceFact]
        Extracted claim facts.

    Returns
    -------
    list[dict[str, Any]]
        Three pass results, each a dict with verdict, explanation, etc.

    Raises
    ------
    RuntimeError
        If GROQ_API_KEY is not configured.
    """
    if _client is None:
        raise RuntimeError("GROQ_API_KEY is not set. Cannot call LLM.")

    # Slight temperature variation across passes for diversity
    temperatures = [0.0, 0.1, 0.2]
    return [
        _single_pass(rejection_reason, clauses, facts, temp)
        for temp in temperatures
    ]
