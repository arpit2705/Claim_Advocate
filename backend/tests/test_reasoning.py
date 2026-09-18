"""
test_reasoning.py — Phase 2A tests for reasoning modules (LLM dependent).
"""
import pytest
from app.reasoning.consistency import tally_consistency, select_best_pass


def test_tally_consistency():
    passes = [
        {"verdict": "valid", "explanation": "A"},
        {"verdict": "valid", "explanation": "B"},
        {"verdict": "questionable", "explanation": "C"}
    ]
    plurality, score, verdicts = tally_consistency(passes)
    assert plurality == "valid"
    assert round(score, 2) == 0.67
    assert verdicts == ["valid", "valid", "questionable"]


def test_tally_consistency_unanimous():
    passes = [
        {"verdict": "likely_misapplied", "explanation": "A"},
        {"verdict": "likely_misapplied", "explanation": "B"},
        {"verdict": "likely_misapplied", "explanation": "C"}
    ]
    plurality, score, _ = tally_consistency(passes)
    assert plurality == "likely_misapplied"
    assert score == 1.0


def test_select_best_pass():
    passes = [
        {"verdict": "valid", "explanation": "Short."},
        {"verdict": "valid", "explanation": "This is a much longer and more detailed explanation."},
        {"verdict": "questionable", "explanation": "Irrelevant longest explanation here..."}
    ]
    best = select_best_pass(passes, "valid")
    assert best["explanation"].startswith("This is a much longer")


@pytest.mark.requires_llm
def test_run_three_pass_reasoning():
    from app.reasoning.policy_evidence_reasoner import run_three_pass_reasoning
    from app.schemas.policy import Clause
    from app.schemas.evidence import EvidenceFact

    clauses = [
        Clause(
            clause_id="CL-1",
            clause_type="exclusion",
            raw_text="No coverage for self-inflicted injuries.",
            trigger_conditions=[],
            page_number=1
        )
    ]
    facts = [
        EvidenceFact(
            fact_id="f1",
            field="diagnosis",
            value="Self-inflicted wound",
            source_document="doc1",
            page=1,
            confidence=0.9
        )
    ]
    rejection_reason = "Denied due to self-inflicted injury exclusion."

    results = run_three_pass_reasoning(rejection_reason, clauses, facts)
    assert len(results) == 3
    for r in results:
        assert r["verdict"] in ["valid", "questionable", "likely_misapplied", "insufficient_evidence"]
        assert "explanation" in r
