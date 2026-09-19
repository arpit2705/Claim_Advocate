"""
explanation_generator.py — Plain-language explanation for valid verdicts.

Only generates explanations when grounded=True (clauses + facts present).
Uses the LLM to rephrase the technical verdict into language a policyholder
can understand. Document text is always passed through sanitizer.
"""
from __future__ import annotations

import json

from groq import Groq

from app.config import GROQ_API_KEY, GROQ_MODEL
from app.extraction.sanitizer import build_safe_prompt
from app.schemas.evidence import EvidenceFact
from app.schemas.policy import Clause
from app.schemas.verdict import Verdict

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

_EXPLANATION_INSTRUCTION = """
You are a consumer advocate helping a policyholder understand an insurance claim decision.
Given the verdict, the relevant policy clause, and the claim facts below, write a clear
2-3 paragraph plain-language explanation of why this decision was reached.

Guidelines:
- Use plain English, avoid jargon.
- Quote specific clause language to ground the explanation.
- Reference specific claim facts that were relevant.
- Do not speculate beyond what the documents state.
- Be neutral and factual — do not editorialize.

Return a JSON object with one key: "explanation" (string).
""".strip()


def generate_explanation(
    verdict: Verdict,
    clauses: list[Clause],
    facts: list[EvidenceFact],
    grounded: bool,
) -> str:
    """
    Generates a plain-language explanation of the adjudication verdict.

    Parameters
    ----------
    verdict : Verdict
        The final validated verdict.
    clauses : list[Clause]
        Retrieved policy clauses.
    facts : list[EvidenceFact]
        Extracted claim facts.
    grounded : bool
        Whether the result is grounded in real clauses and facts.

    Returns
    -------
    str
        Plain-language explanation. Returns a fallback string if not grounded
        or if GROQ_API_KEY is not set.
    """
    if not grounded:
        return (
            f"Verdict: {verdict.verdict}. "
            "This result could not be fully grounded in verified policy clauses "
            "and claim facts. Manual review is recommended."
        )

    if _client is None:
        # Deterministic fallback — no LLM
        return (
            f"Verdict: {verdict.verdict}. "
            f"{verdict.mismatch_explanation or 'See rule results for details.'}"
        )

    matched_clause = next(
        (c for c in clauses if c.clause_id == verdict.matched_clause_id), None
    )
    clause_text = (
        f"[{matched_clause.clause_id}]: {matched_clause.raw_text}"
        if matched_clause
        else "No specific clause was conclusively matched."
    )
    fact_text = "\n".join(
        f"- {f.field}: {f.value} (source: {f.source_document})" for f in facts
    )
    context = (
        f"VERDICT: {verdict.verdict}\n"
        f"MISMATCH EXPLANATION: {verdict.mismatch_explanation}\n\n"
        f"RELEVANT CLAUSE:\n{clause_text}\n\n"
        f"CLAIM FACTS:\n{fact_text}"
    )

    system_prompt, user_prompt = build_safe_prompt(
        task_instruction=_EXPLANATION_INSTRUCTION,
        documents={"verdict_context": context},
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
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        try:
            parsed = json.loads(raw)
            if "explanation" in parsed and parsed["explanation"]:
                return parsed["explanation"]
        except json.JSONDecodeError:
            _log.warning("Explanation generation JSON parse failed (attempt %d). Raw output: %s", attempt + 1, raw)
            continue
            
    return f"Error: Explanation generation failed, please retry. (Technical details: {verdict.mismatch_explanation})"
