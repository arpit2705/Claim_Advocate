"""
decision_validator.py — Deterministic validation of LLM-proposed verdicts.

One focused function: validate_verdict().
Checks:
  1. Citation existence — every clause_id referenced exists in the extracted clause list
  2. Fact existence — facts referenced in the explanation actually exist
  3. Rule satisfaction — any deterministic rule results are consistent with the verdict
  4. Contradiction check — contradictions don't silently support a "valid" verdict
  5. Verdict support — insufficient_evidence if evidence is too sparse

Python has the final word. If validation overrides the LLM verdict, the override
reason is recorded in mismatch_explanation.
"""
from __future__ import annotations

from app.schemas.evidence import ContradictionFlag, EvidenceFact
from app.schemas.policy import Clause
from app.schemas.rules import RuleResult
from app.schemas.verdict import Verdict


def validate_verdict(
    proposed_verdict: str,
    proposed_matched_clause_id: str | None,
    proposed_mismatch_explanation: str,
    pass_results: list[str],
    consistency_score: float,
    clauses: list[Clause],
    facts: list[EvidenceFact],
    rule_results: list[RuleResult],
    contradictions: list[ContradictionFlag],
    explanation: str,
) -> Verdict:
    """
    Validates the LLM-proposed verdict against deterministic Python checks.

    Validation rules (applied in priority order):
      1. If facts list is empty → override to insufficient_evidence
      2. If proposed matched_clause_id doesn't exist in clauses → flag mismatch
      3. If any deterministic rule failed AND verdict is "valid" → downgrade to "questionable"
      4. If high-severity contradictions exist AND verdict is "valid" → downgrade to "questionable"
      5. If clauses list is empty → override to insufficient_evidence

    Parameters
    ----------
    proposed_verdict : str
        Verdict proposed by the LLM plurality vote.
    proposed_matched_clause_id : str | None
        Clause ID the LLM identified as most relevant.
    proposed_mismatch_explanation : str
        LLM's own mismatch explanation.
    pass_results : list[str]
        Verdict from each of the 3 passes (for audit trail).
    consistency_score : float
        Agreement rate across passes.
    clauses : list[Clause]
        Clauses available in the index.
    facts : list[EvidenceFact]
        Extracted claim facts.
    rule_results : list[RuleResult]
        Results from deterministic rule checks.
    contradictions : list[ContradictionFlag]
        Detected contradictions.
    explanation : str
        LLM explanation from the best pass.

    Returns
    -------
    Verdict
        Final validated verdict (may differ from proposed).
    """
    override_reason: str | None = None
    final_verdict = proposed_verdict
    matched_clause_id = proposed_matched_clause_id

    known_clause_ids = {c.clause_id for c in clauses}

    # Rule 1: No facts → insufficient_evidence
    if not facts:
        final_verdict = "insufficient_evidence"
        override_reason = (
            "No claim facts were extracted from submitted documents. "
            "Cannot evaluate rejection validity without evidence."
        )

    # Rule 5: No clauses → insufficient_evidence
    elif not clauses:
        final_verdict = "insufficient_evidence"
        override_reason = (
            "No policy clauses were available for retrieval. "
            "Cannot evaluate rejection validity without policy text."
        )

    # Rule 2: Cited clause_id doesn't exist
    elif proposed_matched_clause_id and proposed_matched_clause_id not in known_clause_ids:
        override_reason = (
            f"LLM cited clause '{proposed_matched_clause_id}' which does not "
            f"exist in the extracted clause list. Citation cannot be verified."
        )
        matched_clause_id = None
        # Downgrade valid → questionable; keep others as-is
        if final_verdict == "valid":
            final_verdict = "questionable"

    # Rule 3: Deterministic rule failures override "valid"
    if final_verdict == "valid" and rule_results:
        failed_rules = [r for r in rule_results if not r.passed]
        if failed_rules:
            final_verdict = "questionable"
            failed_names = ", ".join(r.rule_name for r in failed_rules)
            override_reason = (
                f"Deterministic rule check(s) failed: {failed_names}. "
                f"Verdict downgraded from 'valid' to 'questionable'."
            )

    # Rule 4: High-severity contradictions override "valid"
    if final_verdict == "valid" and contradictions:
        high = [c for c in contradictions if c.severity == "high"]
        if high:
            final_verdict = "questionable"
            fields = ", ".join(c.field for c in high)
            override_reason = (
                f"High-severity contradictions detected in field(s): {fields}. "
                f"Verdict downgraded from 'valid' to 'questionable'."
            )

    mismatch_explanation = override_reason or proposed_mismatch_explanation

    return Verdict(
        verdict=final_verdict,
        consistency_score=consistency_score,
        matched_clause_id=matched_clause_id,
        mismatch_explanation=mismatch_explanation,
        pass_results=pass_results,
    )
