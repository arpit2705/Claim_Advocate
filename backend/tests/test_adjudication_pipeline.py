"""
test_adjudication_pipeline.py — Phase 2A tests for adjudication_engine.py
"""
import pytest
from app.modules.adjudication_engine import run_adjudication_pipeline
from app.schemas.rejection import RejectionRecord
from app.schemas.evidence import EvidenceFact
from app.schemas.policy import Clause
from app.retrieval.embedding_index import ClauseEmbeddingIndex
from app.retrieval.hybrid_retrieval import HybridRetriever


@pytest.fixture
def mock_retriever():
    clauses = [
        Clause(
            clause_id="CL-EXC-1",
            clause_type="exclusion",
            raw_text="Pre-existing conditions within 24 months are not covered.",
            trigger_conditions=["pre-existing condition"],
            page_number=1
        ),
        Clause(
            clause_id="CL-WAIT-1",
            clause_type="waiting_period",
            raw_text="30 day waiting period applies.",
            trigger_conditions=["claim within 30 days"],
            page_number=1
        )
    ]
    idx = ClauseEmbeddingIndex()
    idx.build(clauses)
    return HybridRetriever(idx)


@pytest.mark.requires_llm
def test_pipeline_valid_rejection(mock_retriever):
    rejection = RejectionRecord(
        cited_clause_ref="CL-EXC-1",
        stated_reason="Claim denied because asthma is a pre-existing condition treated 6 months ago.",
        claim_facts=[
            EvidenceFact(fact_id="1", field="diagnosis", value="Asthma", source_document="doc", page=1, confidence=1.0),
            EvidenceFact(fact_id="2", field="previous_treatment_date", value="2023-06-01", source_document="doc", page=1, confidence=1.0) # Within 24m
        ]
    )
    result = run_adjudication_pipeline(rejection, mock_retriever)
    assert result.verdict.verdict in ["valid", "questionable"] # LLM might be slightly lenient, but it shouldn't be likely_misapplied
    assert result.grounded is True
    # Appeal letter should be None if valid
    if result.verdict.verdict == "valid":
        assert result.appeal_letter is None


@pytest.mark.requires_llm
def test_pipeline_misapplied_rejection(mock_retriever):
    rejection = RejectionRecord(
        cited_clause_ref="CL-WAIT-1",
        stated_reason="Claim denied due to 30 day waiting period.",
        claim_facts=[
            EvidenceFact(fact_id="1", field="policy_start_date", value="2020-01-01", source_document="doc", page=1, confidence=1.0),
            EvidenceFact(fact_id="2", field="admission_date", value="2024-01-01", source_document="doc", page=1, confidence=1.0)
        ]
    )
    # The facts clearly show policy started years ago, so 30 day waiting period is irrelevant.
    result = run_adjudication_pipeline(rejection, mock_retriever)
    assert result.verdict.verdict == "likely_misapplied"
    assert result.appeal_letter is not None
    assert "CL-WAIT-1" in result.appeal_letter


@pytest.mark.requires_llm
def test_pipeline_ambiguous_insufficient(mock_retriever):
    rejection = RejectionRecord(
        cited_clause_ref="CL-EXC-1",
        stated_reason="Claim denied for pre-existing condition.",
        claim_facts=[
            # Missing facts about when it was previously treated
            EvidenceFact(fact_id="1", field="diagnosis", value="Unknown Illness", source_document="doc", page=1, confidence=1.0),
        ]
    )
    result = run_adjudication_pipeline(rejection, mock_retriever)
    # The LLM should realize there's not enough evidence to say it's valid or misapplied.
    assert result.verdict.verdict == "insufficient_evidence"


def test_pipeline_ungrounded(mock_retriever):
    rejection = RejectionRecord(
        cited_clause_ref="CL-NONE",
        stated_reason="Denied.",
        claim_facts=[]
    )
    result = run_adjudication_pipeline(rejection, mock_retriever)
    assert result.verdict.verdict == "insufficient_evidence"
    assert result.grounded is False
    assert result.appeal_letter is None
