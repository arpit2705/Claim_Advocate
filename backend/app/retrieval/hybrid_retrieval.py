"""
hybrid_retrieval.py — Combines exact clause_id lookup with semantic search.

Strategy:
  1. If the query is a known clause_id (exact match) → return it directly.
  2. Otherwise run semantic search over the embedding index.
  3. Results from both paths are merged (deduplicated, exact match boosted to top).
"""
from __future__ import annotations

from app.retrieval.embedding_index import ClauseEmbeddingIndex
from app.schemas.policy import Clause


class HybridRetriever:
    """
    Retrieves clauses via exact clause_id lookup and/or semantic similarity.

    Parameters
    ----------
    index : ClauseEmbeddingIndex
        A pre-built embedding index.
    """

    def __init__(self, index: ClauseEmbeddingIndex) -> None:
        self._index = index

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[tuple[Clause, float]]:
        """
        Hybrid retrieval: exact ID lookup + semantic search, merged and deduplicated.

        Parameters
        ----------
        query : str
            Either a clause_id (e.g. "CL-003") or a natural-language description.
        top_k : int
            Maximum number of results to return.

        Returns
        -------
        list[tuple[Clause, float]]
            (clause, score) pairs sorted by score descending.
            Exact match is assigned score 1.0 and placed first.
        """
        results: dict[str, tuple[Clause, float]] = {}

        # 1. Exact ID lookup
        exact = self._index.lookup_by_id(query.strip())
        if exact is not None:
            results[exact.clause_id] = (exact, 1.0)

        # 2. Semantic search (always run, fill remaining slots)
        semantic_hits = self._index.semantic_search(query, top_k=top_k + 1)
        for clause, score in semantic_hits:
            if clause.clause_id not in results:
                results[clause.clause_id] = (clause, score)

        # Sort: exact match (score 1.0) first, then by descending score
        sorted_results = sorted(results.values(), key=lambda x: x[1], reverse=True)
        return sorted_results[:top_k]

    def lookup_by_id(self, clause_id: str) -> Clause | None:
        """Direct passthrough to exact ID lookup."""
        return self._index.lookup_by_id(clause_id)
