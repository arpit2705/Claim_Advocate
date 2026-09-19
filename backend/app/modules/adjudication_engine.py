"""
adjudication_engine.py — Module B Core: Post-Rejection Adjudication.

Orchestrates the pipeline:
  1. Retrieve relevant policy clauses based on the rejection reason.
  2. Run deterministic rules (if applicable) and contradiction checks.
  3. LLM Reasoning (3 passes) proposing a verdict.
  4. Consistency tallying.
  5. Python Validation (overrides LLM if rules/citations fail).
  6. Generate Explanation and (if applicable) Appeal Letter.
"""
from __future__ import annotations

from app.schemas.evidence import EvidenceFact, ContradictionFlag
from app.schemas.policy import Clause
from app.schemas.rejection import RejectionRecord
from app.schemas.rules import RuleResult
from app.schemas.verdict import ClaimAdvocateResult

from app.retrieval.hybrid_retrieval import HybridRetriever
from app.retrieval.query_expansion import expand_rejection_query
from app.rules.contradiction_detector import detect_contradictions
from app.rules.rule_engine import run_all_rules
from app.reasoning.policy_evidence_reasoner import run_three_pass_reasoning
from app.reasoning.consistency import tally_consistency, select_best_pass
from app.validation.decision_validator import validate_verdict
from app.modules.explanation_generator import generate_explanation
from app.modules.appeal_generator import generate_appeal


def run_adjudication_pipeline(
    rejection: RejectionRecord,
    retriever: HybridRetriever,
    rule_inputs: list[dict] = None,
) -> ClaimAdvocateResult:
    """
    Runs the full Module B adjudication pipeline.

    Parameters
    ----------
    rejection : RejectionRecord
        The insurer's rejection details and claim facts.
    retriever : HybridRetriever
        Configured retrieval engine.
    rule_inputs : list[dict], optional
        Deterministic rules to run (if known from context).

    Returns
    -------
    ClaimAdvocateResult
        The final adjudicated result.
    """
    rule_inputs = rule_inputs or []
    facts = rejection.claim_facts

    # 1. Retrieval
    if rejection.cited_clause_ref:
        query = rejection.cited_clause_ref
        expanded_query = query
    else:
        query = rejection.stated_reason
        expanded_query = expand_rejection_query(query)
        
    retrieved_hits = retriever.retrieve(expanded_query, top_k=3)
    clauses = [c for c, _ in retrieved_hits]

    from app.rules.notification_rule import check_notification_timing
    from app.rules.coverage_rule import check_coverage_period_auto
    from app.rules.waiting_period_rule import check_waiting_period_auto
    from app.rules.deadline_rule import check_deadline_auto

    # 2. Deterministic Checks
    contradictions = detect_contradictions(facts)
    
    # Run explicit rule_inputs (from caller)
    explicit_rule_results = run_all_rules(rule_inputs)
    
    # Run auto-detected rules if applicable
    auto_notification = check_notification_timing(rejection, clauses)
    auto_coverage = check_coverage_period_auto(rejection, clauses)
    auto_waiting_period = check_waiting_period_auto(rejection, clauses)
    auto_deadline = check_deadline_auto(rejection, clauses)
    
    # Merge: explicit rules take precedence; auto rules fill in gaps
    rule_results: list = list(explicit_rule_results)
    existing_names = {r.rule_name for r in rule_results}
    
    auto_results = [
        ("notification_timing", auto_notification),
        ("coverage_period_check", auto_coverage),
        ("waiting_period_check", auto_waiting_period),
        ("deadline_check", auto_deadline)
    ]
    
    for name, result in auto_results:
        if result is not None and name not in existing_names:
            rule_results.append(result)
            existing_names.add(name)

    grounded = bool(clauses and facts)

    # 3. LLM Reasoning (skip if completely ungrounded)
    if grounded:
        pass_results = run_three_pass_reasoning(
            rejection_reason=rejection.stated_reason,
            clauses=clauses,
            facts=facts,
            rule_results=rule_results,
        )
        plurality_verdict, consistency_score, pass_verdict_list = tally_consistency(pass_results)
        best_pass = select_best_pass(pass_results, plurality_verdict)
        proposed_verdict = best_pass.get("verdict", "insufficient_evidence")
        proposed_matched_id = best_pass.get("matched_clause_id")
        proposed_mismatch_expl = best_pass.get("mismatch_explanation", "")
        proposed_explanation = best_pass.get("explanation", "")
    else:
        proposed_verdict = "insufficient_evidence"
        proposed_matched_id = None
        proposed_mismatch_expl = "Missing fundamental evidence or policy clauses."
        proposed_explanation = ""
        pass_verdict_list = []
        consistency_score = 0.0

    # 4. Python Validation
    final_verdict_obj = validate_verdict(
        proposed_verdict=proposed_verdict,
        proposed_matched_clause_id=proposed_matched_id,
        proposed_mismatch_explanation=proposed_mismatch_expl,
        pass_results=pass_verdict_list,
        consistency_score=consistency_score,
        clauses=clauses,
        facts=facts,
        rule_results=rule_results,
        contradictions=contradictions,
        explanation=proposed_explanation,
    )

    # 5. Generation
    final_explanation = generate_explanation(
        verdict=final_verdict_obj,
        clauses=clauses,
        facts=facts,
        grounded=grounded,
    )
    
    appeal_letter = generate_appeal(
        verdict=final_verdict_obj,
        clauses=clauses,
        facts=facts,
        rejection_reason=rejection.stated_reason,
        grounded=grounded,
    )

    matched_clause = None
    if final_verdict_obj.matched_clause_id:
        matched_clause = next(
            (c for c in clauses if c.clause_id == final_verdict_obj.matched_clause_id),
            None
        )
    # Grounding guard: if LLM returned no matched_clause_id but we retrieved clauses,
    # assign the top-scored retrieved clause so the UI never shows "Clause text not found"
    if matched_clause is None and clauses:
        import logging
        _log = logging.getLogger(__name__)
        _log.warning(
            "LLM did not set matched_clause_id. Falling back to top retrieved clause: %s",
            clauses[0].clause_id
        )
        matched_clause = clauses[0]
        # Patch the verdict's matched_clause_id to match
        from app.schemas.verdict import Verdict
        final_verdict_obj = Verdict(
            verdict=final_verdict_obj.verdict,
            consistency_score=final_verdict_obj.consistency_score,
            matched_clause_id=matched_clause.clause_id,
            mismatch_explanation=final_verdict_obj.mismatch_explanation,
            pass_results=final_verdict_obj.pass_results,
        )

    return ClaimAdvocateResult(
        verdict=final_verdict_obj,
        contradictions=contradictions,
        rule_results=rule_results,
        grounded=grounded,
        explanation=final_explanation,
        appeal_letter=appeal_letter,
        matched_clause=matched_clause,
        referenced_facts=facts,
        insurer_stated_reason=rejection.stated_reason,
    )
