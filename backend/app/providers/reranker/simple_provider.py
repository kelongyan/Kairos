"""Deterministic fallback reranker.

This provider gives Kairos a true second-stage rerank step without adding
remote dependencies. It scores candidate chunks by lexical overlap against the
query and prefers concise chunks with stronger overlap. The interface remains
compatible with a future model-based reranker provider.
"""

from __future__ import annotations

import re
from collections import Counter

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


class SimpleRerankerProvider:
    """Fallback reranker based on lexical overlap and brevity."""

    def rerank(
        self,
        query: str,
        documents: list[str],
        top_k: int = 8,
    ) -> list[tuple[int, float]]:
        query_counts = Counter(_tokenize(query))
        if not query_counts:
            return []

        scored: list[tuple[int, float]] = []
        for idx, text in enumerate(documents):
            token_counts = Counter(_tokenize(text))
            overlap = sum(min(token_counts[t], count) for t, count in query_counts.items())
            if overlap <= 0:
                continue
            length_penalty = max(len(token_counts), 1)
            score = overlap / length_penalty
            scored.append((idx, float(score)))

        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text)]
