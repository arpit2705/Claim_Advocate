"""
embedding_index.py — In-memory clause embedding index using sentence-transformers.

Builds embeddings for all Clause objects and provides:
  - exact lookup by clause_id  (O(1) dict)
  - semantic nearest-neighbour search via cosine similarity (pure numpy, no external DB)
"""
from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL
from app.schemas.policy import Clause

# Lazy-loaded singleton model to avoid repeated heavy initialisation
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


class ClauseEmbeddingIndex:
    """
    In-memory embedding index for a list of Clause objects.

    Attributes
    ----------
    clauses : list[Clause]
        The indexed clauses.
    _id_map : dict[str, Clause]
        Fast O(1) lookup by clause_id.
    _embeddings : np.ndarray | None
        Matrix of shape (N, D) — one row per clause.
    """

    def __init__(self) -> None:
        self.clauses: list[Clause] = []
        self._id_map: dict[str, Clause] = {}
        self._embeddings: np.ndarray | None = None

    def build(self, clauses: list[Clause]) -> None:
        """
        Index a list of clauses. Computes embeddings for all raw_text fields.

        Parameters
        ----------
        clauses : list[Clause]
            Clauses to index. Replaces any previously indexed clauses.
        """
        self.clauses = clauses
        self._id_map = {c.clause_id: c for c in clauses}

        if not clauses:
            self._embeddings = None
            return

        model = _get_model()
        texts = [c.raw_text for c in clauses]
        self._embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    def lookup_by_id(self, clause_id: str) -> Clause | None:
        """
        Exact lookup by clause_id.

        Parameters
        ----------
        clause_id : str
            The clause_id to look up.

        Returns
        -------
        Clause | None
            The clause if found, else None.
        """
        return self._id_map.get(clause_id)

    def semantic_search(self, query: str, top_k: int = 3) -> list[tuple[Clause, float]]:
        """
        Returns the top_k clauses most semantically similar to query.

        Parameters
        ----------
        query : str
            Natural language query / paraphrase.
        top_k : int
            Number of results to return.

        Returns
        -------
        list[tuple[Clause, float]]
            List of (clause, cosine_similarity_score) sorted descending.
        """
        if self._embeddings is None or len(self.clauses) == 0:
            return []

        model = _get_model()
        q_emb = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
        # Cosine similarity: embeddings are already L2-normalised → dot product
        scores: np.ndarray = (self._embeddings @ q_emb.T).flatten()
        top_indices = np.argsort(scores)[::-1][: min(top_k, len(self.clauses))]
        return [(self.clauses[i], float(scores[i])) for i in top_indices]

    def __len__(self) -> int:
        return len(self.clauses)
