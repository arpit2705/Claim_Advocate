"""
test_readiness_pipeline.py — Phase 2B tests for readiness_engine.py
"""
import pytest
from app.modules.readiness_engine import run_readiness_pipeline
from app.schemas.evidence import SubmissionEvidence, EvidenceFact


@pytest.fixture
def base_evidence():
    return SubmissionEvidence(
        claim_type="medical",
        facts=[
            EvidenceFact(fact_id="1", field="admission_date", value="2024-01-01", source_document="doc", page=1, confidence=1.0),
            EvidenceFact(fact_id="2", field="claim_amount", value="5000", source_document="doc", page=1, confidence=1.0)
        ],
        documents_provided=["doc"]
    )


def test_genuinely_ready(base_evidence):
    result = run_readiness_pipeline(
        submission=base_evidence,
        rule_inputs=[],
        required_fields=["admission_date", "claim_amount"]
    )
    # 50 critical + 30 evidence + 15 consistency + 5 supporting
    assert result.readiness_score == 100.0
    assert result.grounded is True
    assert len(result.prioritized_fixes) == 0


def test_missing_document(base_evidence):
    result = run_readiness_pipeline(
        submission=base_evidence,
        rule_inputs=[],
        required_fields=["admission_date", "claim_amount", "discharge_summary"]
    )
    # penalty for 1 missing field out of 3 = 10 points off evidence score
    assert result.readiness_score == 90.0
    assert "discharge_summary" in result.missing_evidence
    assert any("Missing required information" in f for f in result.prioritized_fixes)


def test_contradictory_dates(base_evidence):
    # Add a contradictory admission date
    base_evidence.facts.append(
        EvidenceFact(fact_id="3", field="admission_date", value="2024-01-02", source_document="doc2", page=1, confidence=1.0)
    )
    result = run_readiness_pipeline(
        submission=base_evidence,
        rule_inputs=[],
        required_fields=["admission_date"]
    )
    # high severity contradiction -> 10 points off consistency
    assert result.readiness_score == 90.0
    assert len(result.contradictions) == 1
    assert any("Critical contradiction" in f for f in result.prioritized_fixes)


def test_rule_failure(base_evidence):
    from datetime import date
    result = run_readiness_pipeline(
        submission=base_evidence,
        rule_inputs=[
            {"rule": "deadline", "incident_date": date(2023, 1, 1), "submission_date": date(2024, 1, 1), "deadline_days": 30}
        ],
        required_fields=["admission_date"]
    )
    # critical rule failure drops score by 50 (if 1 rule)
    assert result.readiness_score == 50.0
    assert len(result.rule_results) == 1
    assert result.rule_results[0].passed is False
    assert any("Rule failed" in f for f in result.prioritized_fixes)


def test_ungrounded_empty():
    empty_ev = SubmissionEvidence(claim_type="medical", facts=[], documents_provided=[])
    result = run_readiness_pipeline(
        submission=empty_ev,
        rule_inputs=[],
        required_fields=["admission_date"]
    )
    assert result.grounded is False
    assert result.readiness_score == 65.0  # (50 critical + 0 evidence (1/1 missing) + 15 consistency + 0 supporting)
    assert any("No evidence facts could be extracted" in f for f in result.prioritized_fixes)
