"""Query rewrite helpers for Phase 2 hybrid RAG.

The first version intentionally stays lightweight: preserve the original query,
apply minimal whitespace normalization, and expose a stable seam for future
LLM-based rewrite/decomposition without changing chat orchestration.
"""

from __future__ import annotations


def rewrite_query(question: str) -> str:
    """Return a normalized rewrite of the user's question.

    Phase 2 starts with a deterministic rewrite so retrieval trace, caching, and
    tests can rely on a stable contract before introducing model-based rewrite.
    """
    return " ".join(question.split())
