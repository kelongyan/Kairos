"""Sparse retrieval service for Phase 2 hybrid RAG.

Uses BM25 over indexed chunk text stored in PostgreSQL rows. The service
boundary stays separate from dense retrieval so this implementation can later
be replaced by another sparse engine without changing orchestration.
"""

from __future__ import annotations

import re

from rank_bm25 import BM25Okapi
from sqlalchemy.orm import Session

from app.repositories import document_repo
from app.services.vector_service import RetrievedChunk

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def retrieve_sparse(
    db: Session,
    query: str,
    *,
    doc_id: str,
    top_k: int,
) -> list[RetrievedChunk]:
    """Retrieve chunks by BM25 within a single document."""
    chunks = document_repo.list_chunks(db, doc_id)
    if not chunks:
        return []

    tokenized_corpus = [_tokenize(chunk.text) for chunk in chunks]
    query_terms = _tokenize(query)
    if not query_terms:
        return []

    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(query_terms)

    ranked = sorted(
        (
            (float(score), chunk)
            for score, chunk in zip(scores, chunks, strict=True)
            if score > 0
        ),
        key=lambda item: item[0],
        reverse=True,
    )[:top_k]

    return [
        RetrievedChunk(
            chunk_id=chunk.chunk_id,
            doc_id=chunk.doc_id,
            text=chunk.text,
            section=chunk.section,
            page_start=chunk.page_start,
            page_end=chunk.page_end,
            chunk_type=chunk.chunk_type,
            chunk_index=chunk.chunk_index,
            score=score,
        )
        for score, chunk in ranked
    ]


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in _TOKEN_RE.findall(text)]
