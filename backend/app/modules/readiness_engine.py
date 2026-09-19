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

WEIGHT_CRITICAL = 50.0
WEIGHT_EVIDENCE = 30.0
WEIGHT_CONSISTENCY = 15.0
WEIGHT_SUPPORTING = 5.0

def run_readiness_pipeline(
    submission: SubmissionEvidence,
    rule_inputs: list[dict] = None,
    required_fields: list[str] = None,
) -> ReadinessResult:
    """
    Evaluates claim readiness prior to submission.
    """
    rule_inputs = rule_inputs or []
    required_fields = required_fields or []
    
    facts = submission.facts
    rule_results = run_all_rules(rule_inputs)
    contradictions = detect_contradictions(facts)

    fixes = []
    missing_evidence = []
    
    # ── Document Inventory ──
    # Map from standard names to known files uploaded
    expected_docs = ["claim_form", "discharge_summary", "hospital_bill", "prescription", "investigation_report", "identity_proof"]
    detected_docs_set = set()
    for doc in submission.documents_provided:
        lower_doc = doc.lower()
        for exp in expected_docs:
            if exp.replace("_", " ") in lower_doc or exp in lower_doc:
                detected_docs_set.add(exp)
        # generic catch-all for unknown docs
        detected_docs_set.add(doc)

    missing_docs = [d for d in expected_docs if d not in detected_docs_set]
    detected_docs_list = list(detected_docs_set)
    
    for md in missing_docs:
        fixes.append(f"Missing required document: {md.replace('_', ' ').capitalize()}")

    # Check required fields
    extracted_fields = {f.field.lower() for f in facts}
    for req in required_fields:
        if req.lower() not in extracted_fields:
            missing_evidence.append(req)

    # ── Score Breakdown ──
    score_breakdown = []
    total_score = 0.0
    
    # We assign 20 points per check if it passes.
    # We have 4 rule checks.
    base_weight = 20.0
    for r in rule_results:
        if r.status == "PASS":
            contribution = base_weight
        elif r.status == "PARTIAL":
            contribution = base_weight / 2.0
        else:
            contribution = 0.0
            
        score_breakdown.append({
            "check": r.rule_name,
            "status": r.status,
            "weight": base_weight,
            "contribution": contribution,
            "reason": r.explanation if r.status != "PASS" else None
        })
        total_score += contribution
        
        if r.status == "FAIL":
            fixes.append(f"Rule failed ({r.rule_name}): {r.explanation}")

    # Give 20 points for document completeness
    doc_contribution = 20.0 if not missing_docs else max(0, 20.0 - (len(missing_docs) * 5))
    score_breakdown.append({
        "check": "document_completeness",
        "status": "PASS" if not missing_docs else "PARTIAL",
        "weight": 20.0,
        "contribution": doc_contribution,
        "reason": f"Missing {len(missing_docs)} required documents" if missing_docs else None
    })
    total_score += doc_contribution

    # ── Consistency & Verification Status ──
    has_high_severity_contradiction = False
    for c in contradictions:
        if c.severity == "high":
            has_high_severity_contradiction = True
            fixes.append(f"CRITICAL: Contradiction in {c.field}: {c.value_a} vs {c.value_b}")
        else:
            fixes.append(f"Contradiction in {c.field}: {c.value_a} vs {c.value_b}")

    has_unknowns = any(r.status in ("UNKNOWN", "PARTIAL") for r in rule_results)
    
    if has_high_severity_contradiction or "FAIL" in [r.status for r in rule_results]:
        verification_status = "REQUIRES_REVIEW"
    elif has_unknowns or missing_docs or missing_evidence:
        verification_status = "PARTIALLY_VERIFIED"
    else:
        verification_status = "FULLY_VERIFIED"

    if not facts:
        fixes.append("No evidence facts could be extracted.")
        verification_status = "REQUIRES_REVIEW"

    return ReadinessResult(
        readiness_score=round(total_score, 1),
        verification_status=verification_status,
        rule_results=rule_results,
        contradictions=contradictions,
        detected_documents=detected_docs_list,
        missing_documents=missing_docs,
        missing_evidence=missing_evidence,
        prioritized_fixes=fixes,
        score_breakdown=score_breakdown,
    )
