"""
test_validation.py — Phase 2A tests for decision_validator.py
"""
import pytest
from app.validation.decision_validator import validate_verdict
from app.schemas.evidence import EvidenceFact, ContradictionFlag
from app.schemas.policy import Clause
from app.schemas.rules import RuleResult


@pytest.fixture
def base_facts():
    return [EvidenceFact(fact_id="1", field="test", value="test", source_document="doc", page=1, confidence=1.0)]


@pytest.fixture
def base_clauses():
    return [Clause(clause_id="CL-1", clause_type="coverage", raw_text="test", trigger_conditions=[], page_number=1)]


def test_validator_no_facts(base_clauses):
    verdict = validate_verdict(
        proposed_verdict="valid",
        proposed_matched_clause_id="CL-1",
        proposed_mismatch_explanation="",
        pass_results=["valid"]*3,
        consistency_score=1.0,
        clauses=base_clauses,
        facts=[],  # Empty facts
        rule_results=[],
        contradictions=[],
        explanation=""
    )
    assert verdict.verdict == "insufficient_evidence"
    assert "No claim facts" in verdict.mismatch_explanation


def test_validator_no_clauses(base_facts):
    verdict = validate_verdict(
        proposed_verdict="valid",
        proposed_matched_clause_id="CL-1",
        proposed_mismatch_explanation="",
        pass_results=["valid"]*3,
        consistency_score=1.0,
        clauses=[], # Empty clauses
        facts=base_facts,
        rule_results=[],
        contradictions=[],
        explanation=""
    )
    assert verdict.verdict == "insufficient_evidence"
    assert "No policy clauses" in verdict.mismatch_explanation


def test_validator_invalid_clause_id(base_clauses, base_facts):
    verdict = validate_verdict(
        proposed_verdict="valid",
        proposed_matched_clause_id="CL-999", # Doesn't exist
        proposed_mismatch_explanation="",
        pass_results=["valid"]*3,
        consistency_score=1.0,
        clauses=base_clauses,
        facts=base_facts,
        rule_results=[],
        contradictions=[],
        explanation=""
    )
    assert verdict.verdict == "questionable"
    assert verdict.matched_clause_id is None
    assert "does not exist" in verdict.mismatch_explanation


def test_validator_rule_failure_downgrades_valid(base_clauses, base_facts):
    rules = [RuleResult(rule_name="deadline", passed=False, explanation="Late.")]
    verdict = validate_verdict(
        proposed_verdict="valid",
        proposed_matched_clause_id="CL-1",
        proposed_mismatch_explanation="",
        pass_results=["valid"]*3,
        consistency_score=1.0,
        clauses=base_clauses,
        facts=base_facts,
        rule_results=rules,
        contradictions=[],
        explanation=""
    )
    assert verdict.verdict == "questionable"
    assert "Deterministic rule check(s) failed" in verdict.mismatch_explanation


def test_validator_high_contradiction_downgrades_valid(base_clauses, base_facts):
    contras = [ContradictionFlag(field="date", value_a="1", source_a="a", value_b="2", source_b="b", severity="high", note="")]
    verdict = validate_verdict(
        proposed_verdict="valid",
        proposed_matched_clause_id="CL-1",
        proposed_mismatch_explanation="",
        pass_results=["valid"]*3,
        consistency_score=1.0,
        clauses=base_clauses,
        facts=base_facts,
        rule_results=[],
        contradictions=contras,
        explanation=""
    )
    assert verdict.verdict == "questionable"
    assert "High-severity contradictions" in verdict.mismatch_explanation


def test_validator_passes_clean(base_clauses, base_facts):
    verdict = validate_verdict(
        proposed_verdict="valid",
        proposed_matched_clause_id="CL-1",
        proposed_mismatch_explanation="",
        pass_results=["valid"]*3,
        consistency_score=1.0,
        clauses=base_clauses,
        facts=base_facts,
        rule_results=[],
        contradictions=[],
        explanation="Everything is good."
    )
    assert verdict.verdict == "valid"
    assert verdict.matched_clause_id == "CL-1"
