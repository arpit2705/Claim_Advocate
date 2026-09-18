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
    query = rejection.cited_clause_ref if rejection.cited_clause_ref else rejection.stated_reason
    retrieved_hits = retriever.retrieve(query, top_k=3)
    clauses = [c for c, _ in retrieved_hits]

    # 2. Deterministic Checks
    contradictions = detect_contradictions(facts)
    rule_results = run_all_rules(rule_inputs)

    grounded = bool(clauses and facts)

    # 3. LLM Reasoning (skip if completely ungrounded)
    if grounded:
        pass_results = run_three_pass_reasoning(
            rejection_reason=rejection.stated_reason,
            clauses=clauses,
            facts=facts,
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

    return ClaimAdvocateResult(
        verdict=final_verdict_obj,
        contradictions=contradictions,
        rule_results=rule_results,
        grounded=grounded,
        explanation=final_explanation,
        appeal_letter=appeal_letter,
    )
