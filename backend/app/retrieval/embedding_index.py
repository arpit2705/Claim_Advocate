"""
Lightweight in-memory clause retrieval index.

Uses token-overlap / TF-IDF-style scoring instead of
sentence-transformers so the API can run on low-memory
deployment instances such as Render Free.
"""

from __future__ import annotations

import math
import re
from collections import Counter

from app.schemas.policy import Clause


def _tokenize(text: str) -> list[str]:
    """Simple lightweight tokenizer."""
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


class ClauseEmbeddingIndex:
    """
    Lightweight clause index.

    Provides:
    - exact lookup by clause_id
    - text-based similarity search
    - no PyTorch
    - no sentence-transformers
    """

    def __init__(self) -> None:
        self.clauses: list[Clause] = []
        self._id_map: dict[str, Clause] = {}
        self._documents: list[Counter] = []
        self._idf: dict[str, float] = {}

    def build(self, clauses: list[Clause]) -> None:
        """Index clauses using lightweight token statistics."""

        self.clauses = clauses
        self._id_map = {c.clause_id: c for c in clauses}

        self._documents = []
        self._idf = {}

        if not clauses:
            return

        # Tokenize each clause
        for clause in clauses:
            tokens = _tokenize(clause.raw_text)
            self._documents.append(Counter(tokens))

        # Calculate lightweight IDF
        document_count = len(self._documents)
        document_frequency: Counter = Counter()

        for doc in self._documents:
            for token in doc:
                document_frequency[token] += 1

        for token, df in document_frequency.items():
            self._idf[token] = math.log(
                (document_count + 1) / (df + 1)
            ) + 1.0

    def lookup_by_id(self, clause_id: str) -> Clause | None:
        """Exact O(1) clause lookup."""
        return self._id_map.get(clause_id)

    def _score(self, query_tokens: list[str], document: Counter) -> float:
        """Calculate lightweight TF-IDF-style similarity."""

        if not query_tokens or not document:
            return 0.0

        query_counts = Counter(query_tokens)

        query_vector = {}
        doc_vector = {}

        for token, count in query_counts.items():
            if token in self._idf:
                query_vector[token] = count * self._idf[token]

        for token, count in document.items():
            if token in self._idf:
                doc_vector[token] = count * self._idf[token]

        if not query_vector or not doc_vector:
            return 0.0

        # Dot product
        dot = sum(
            query_vector.get(token, 0.0) * doc_vector.get(token, 0.0)
            for token in query_vector
        )

        # Magnitudes
        query_norm = math.sqrt(
            sum(value * value for value in query_vector.values())
        )

        doc_norm = math.sqrt(
            sum(value * value for value in doc_vector.values())
        )

        if query_norm == 0 or doc_norm == 0:
            return 0.0

        return dot / (query_norm * doc_norm)

    def semantic_search(
        self,
        query: str,
        top_k: int = 3
    ) -> list[tuple[Clause, float]]:
        """
        Return the top-k clauses using lightweight text similarity.

        Keeps the same return format as the previous
        sentence-transformer implementation.
        """

        if not self.clauses:
            return []

        query_tokens = _tokenize(query)

        scored = []

        for clause, document in zip(self.clauses, self._documents):
            score = self._score(query_tokens, document)
            scored.append((clause, score))

        scored.sort(key=lambda item: item[1], reverse=True)

        return scored[:min(top_k, len(scored))]

    def __len__(self) -> int:
        return len(self.clauses)