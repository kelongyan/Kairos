"""Reranker provider factory."""

from __future__ import annotations

from functools import lru_cache

from app.core.config import get_settings
from app.providers.base import RerankerProvider
from app.providers.reranker.simple_provider import SimpleRerankerProvider


@lru_cache
def get_reranker_provider() -> RerankerProvider:
    settings = get_settings()
    provider = settings.reranker_provider.lower()

    if provider == "simple":
        return SimpleRerankerProvider()

    msg = f"Unknown reranker_provider: {provider!r}. Use simple."
    raise ValueError(msg)
