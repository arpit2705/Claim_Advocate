"""
test_retrieval.py — Phase 1 tests for embedding_index and hybrid_retrieval.

Deterministic tests (no LLM):
  - Exact clause_id lookup returns correct clause
  - Unknown clause_id returns None
  - Semantic search returns a sensible top match for paraphrased query
  - Hybrid retrieval: exact match is scored 1.0 and ranked first
  - Empty index returns empty results
"""
import pytest

from app.schemas.policy import Clause
from app.retrieval.embedding_index import ClauseEmbeddingIndex
from app.retrieval.hybrid_retrieval import HybridRetriever

# ── Fixtures ──────────────────────────────────────────────────────────────────

SAMPLE_CLAUSES = [
    Clause(
        clause_id="CL-001",
        clause_type="exclusion",
        raw_text=(
            "Pre-existing conditions diagnosed or treated within 24 months "
            "prior to policy commencement are excluded from coverage."
        ),
        trigger_conditions=["pre-existing condition"],
        page_number=3,
    ),
    Clause(
        clause_id="CL-002",
        clause_type="waiting_period",
        raw_text=(
            "A mandatory 30-day waiting period applies from the policy start "
            "date. Illness claims arising in this window are not covered."
        ),
        trigger_conditions=["illness within 30 days of policy start"],
        page_number=5,
    ),
    Clause(
        clause_id="CL-003",
        clause_type="sub_limit",
        raw_text=(
            "Hospital room rent reimbursement is capped at INR 5,000 per day. "
            "Charges exceeding this limit are the insured's responsibility."
        ),
        trigger_conditions=["room rent claimed"],
        page_number=7,
    ),
    Clause(
        clause_id="CL-004",
        clause_type="coverage",
        raw_text=(
            "Surgical procedures performed by a registered surgeon at an "
            "empanelled hospital are covered up to the sum insured."
        ),
        trigger_conditions=["surgical procedure claimed"],
        page_number=9,
    ),
]


@pytest.fixture(scope="module")
def built_index() -> ClauseEmbeddingIndex:
    idx = ClauseEmbeddingIndex()
    idx.build(SAMPLE_CLAUSES)
    return idx


@pytest.fixture(scope="module")
def retriever(built_index) -> HybridRetriever:
    return HybridRetriever(built_index)


# ── Embedding index tests ─────────────────────────────────────────────────────

class TestClauseEmbeddingIndex:

    def test_build_populates_clauses(self, built_index):
        assert len(built_index) == 4

    def test_exact_lookup_known_id(self, built_index):
        clause = built_index.lookup_by_id("CL-001")
        assert clause is not None
        assert clause.clause_id == "CL-001"
        assert clause.clause_type == "exclusion"

    def test_exact_lookup_another_id(self, built_index):
        clause = built_index.lookup_by_id("CL-003")
        assert clause is not None
        assert clause.clause_id == "CL-003"
        assert clause.clause_type == "sub_limit"

    def test_exact_lookup_unknown_id_returns_none(self, built_index):
        assert built_index.lookup_by_id("CL-999") is None

    def test_semantic_search_returns_results(self, built_index):
        results = built_index.semantic_search("waiting period before claim", top_k=3)
        assert len(results) > 0

    def test_semantic_search_top_match_waiting_period(self, built_index):
        """Paraphrase of the waiting period clause should match CL-002."""
        results = built_index.semantic_search(
            "mandatory waiting period illness not covered in first month", top_k=1
        )
        assert len(results) == 1
        top_clause, score = results[0]
        assert top_clause.clause_id == "CL-002", (
            f"Expected CL-002 (waiting_period) as top match, got {top_clause.clause_id}"
        )
        assert score > 0.3, f"Similarity score too low: {score}"

    def test_semantic_search_room_rent_query(self, built_index):
        """Query about room charges should surface the sub_limit clause."""
        results = built_index.semantic_search(
            "daily room charge limit hospital accommodation", top_k=2
        )
        clause_ids = [c.clause_id for c, _ in results]
        assert "CL-003" in clause_ids, (
            f"Expected CL-003 in top results for room rent query, got: {clause_ids}"
        )

    def test_semantic_search_scores_are_floats(self, built_index):
        results = built_index.semantic_search("surgical coverage", top_k=4)
        for clause, score in results:
            assert isinstance(score, float)
            assert -1.0 <= score <= 1.0

    def test_empty_index_semantic_search(self):
        empty_idx = ClauseEmbeddingIndex()
        empty_idx.build([])
        assert empty_idx.semantic_search("anything") == []

    def test_empty_index_lookup(self):
        empty_idx = ClauseEmbeddingIndex()
        empty_idx.build([])
        assert empty_idx.lookup_by_id("CL-001") is None


# ── Hybrid retriever tests ────────────────────────────────────────────────────

class TestHybridRetriever:

    def test_exact_id_query_returns_score_one(self, retriever):
        results = retriever.retrieve("CL-001", top_k=3)
        assert len(results) > 0
        top_clause, top_score = results[0]
        assert top_clause.clause_id == "CL-001"
        assert top_score == 1.0

    def test_exact_id_ranked_first(self, retriever):
        """Even if semantically similar clauses exist, exact match comes first."""
        results = retriever.retrieve("CL-003", top_k=3)
        assert results[0][0].clause_id == "CL-003"

    def test_semantic_query_no_exact_match(self, retriever):
        results = retriever.retrieve(
            "conditions excluded before policy began", top_k=2
        )
        assert len(results) > 0
        # Should surface the exclusion clause
        clause_ids = [c.clause_id for c, _ in results]
        assert "CL-001" in clause_ids

    def test_no_duplicates_in_results(self, retriever):
        results = retriever.retrieve("CL-002", top_k=4)
        ids = [c.clause_id for c, _ in results]
        assert len(ids) == len(set(ids)), "Duplicate clauses in results"

    def test_top_k_respected(self, retriever):
        results = retriever.retrieve("coverage surgery hospital", top_k=2)
        assert len(results) <= 2

    def test_passthrough_lookup(self, retriever):
        clause = retriever.lookup_by_id("CL-004")
        assert clause is not None
        assert clause.clause_type == "coverage"
