"""
readiness_engine.py — Module A Core: Pre-Submission Readiness.

Computes a weighted readiness score and prioritized fix list based on:
  - Critical Requirements (50%) -> e.g., missing critical documents, rule check failures
  - Required Evidence (30%) -> e.g., presence of needed facts
  - Consistency (15%) -> e.g., contradictions across documents
  - Supporting Evidence (5%) -> e.g., confidence of facts

Prototype weighted scoring model — not a certified readiness determination.
"""
from __future__ import annotations

from app.schemas.evidence import SubmissionEvidence
from app.schemas.readiness import ReadinessResult
from app.rules.contradiction_detector import detect_contradictions
from app.rules.rule_engine import run_all_rules


def run_readiness_pipeline(
    submission: SubmissionEvidence,
    rule_inputs: list[dict] = None,
    required_fields: list[str] = None,
) -> ReadinessResult:
    """
    Evaluates claim readiness prior to submission.

    Parameters
    ----------
    submission : SubmissionEvidence
        The extracted facts and provided documents.
    rule_inputs : list[dict], optional
        Deterministic rules to check (e.g., deadline, waiting period).
    required_fields : list[str], optional
        Expected fields that must be present (e.g., ["admission_date", "claim_amount"]).

    Returns
    -------
    ReadinessResult
        The scored readiness result and fixes.
    """
    rule_inputs = rule_inputs or []
    required_fields = required_fields or []
    
    facts = submission.facts
    rule_results = run_all_rules(rule_inputs)
    contradictions = detect_contradictions(facts)

    fixes = []
    missing = []
    
    # Check required fields
    extracted_fields = {f.field.lower() for f in facts}
    for req in required_fields:
        if req.lower() not in extracted_fields:
            missing.append(req)
            fixes.append(f"Missing required information: {req}")

    # Evaluate Rules (Critical - 50%)
    critical_score = 50.0
    for r in rule_results:
        if not r.passed:
            critical_score -= (50.0 / max(1, len(rule_results)))
            fixes.append(f"Rule failed ({r.rule_name}): {r.explanation}")
    critical_score = max(0.0, critical_score)

    # Evaluate Evidence Completeness (Required - 30%)
    evidence_score = 30.0
    if required_fields:
        penalty = (len(missing) / len(required_fields)) * 30.0
        evidence_score -= penalty
    evidence_score = max(0.0, evidence_score)

    # Evaluate Consistency (Consistency - 15%)
    consistency_score = 15.0
    for c in contradictions:
        if c.severity == "high":
            consistency_score -= 10.0
            fixes.insert(0, f"Critical contradiction in {c.field}: {c.value_a} vs {c.value_b}")
        elif c.severity == "medium":
            consistency_score -= 5.0
            fixes.append(f"Contradiction in {c.field}: {c.value_a} vs {c.value_b}")
        else:
            consistency_score -= 1.0
    consistency_score = max(0.0, consistency_score)

    # Evaluate Confidence (Supporting - 5%)
    supporting_score = 0.0
    if facts:
        avg_conf = sum(f.confidence for f in facts) / len(facts)
        supporting_score = avg_conf * 5.0

    total_score = critical_score + evidence_score + consistency_score + supporting_score
    grounded = len(facts) > 0

    if not grounded:
        fixes.append("No evidence facts could be extracted.")

    return ReadinessResult(
        readiness_score=round(total_score, 1),
        rule_results=rule_results,
        contradictions=contradictions,
        missing_evidence=missing,
        prioritized_fixes=fixes,
        grounded=grounded,
    )
