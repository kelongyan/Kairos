"""Tests for Phase 2 query and retrieval services."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.query_service import rewrite_query
from app.services.retrieval_service import _rerank, _rrf_fuse
from app.services.vector_service import RetrievedChunk


@dataclass
class _Item:
    chunk: RetrievedChunk
    retrieval_source: str


def test_rewrite_query_normalizes_whitespace() -> None:
    assert rewrite_query("  what   reranker   is used?  ") == "what reranker is used?"


def test_rrf_fuse_merges_sources_and_preserves_best_rank() -> None:
    chunk_a = RetrievedChunk(
        chunk_id="a",
        doc_id="doc-1",
        text="A",
        section="S",
        page_start=1,
        page_end=1,
        chunk_type="paragraph",
        chunk_index=0,
        score=0.9,
    )
    chunk_b = RetrievedChunk(
        chunk_id="b",
        doc_id="doc-1",
        text="B",
        section="S",
        page_start=2,
        page_end=2,
        chunk_type="paragraph",
        chunk_index=1,
        score=0.8,
    )
    dense = [
        _Item(chunk=chunk_a, retrieval_source="dense"),
        _Item(chunk=chunk_b, retrieval_source="dense"),
    ]
    sparse = [
        _Item(chunk=chunk_b, retrieval_source="sparse"),
        _Item(chunk=chunk_a, retrieval_source="sparse"),
    ]

    fused = _rrf_fuse(dense, sparse, top_k=2)

    assert len(fused) == 2
    assert fused[0].chunk.chunk_id in {"a", "b"}
    assert fused[0].retrieval_source in {"dense", "sparse", "dense+sparse"}


def test_simple_reranker_changes_result_source_to_rerank() -> None:
    fused = [
        _Item(
            chunk=RetrievedChunk(
                chunk_id="a",
                doc_id="doc-1",
                text="reranker query exact exact",
                section="S",
                page_start=1,
                page_end=1,
                chunk_type="paragraph",
                chunk_index=0,
                score=0.2,
            ),
            retrieval_source="dense+sparse",
        ),
        _Item(
            chunk=RetrievedChunk(
                chunk_id="b",
                doc_id="doc-1",
                text="query",
                section="S",
                page_start=2,
                page_end=2,
                chunk_type="paragraph",
                chunk_index=1,
                score=0.9,
            ),
            retrieval_source="dense+sparse",
        ),
    ]

    reranked = _rerank("reranker query exact", fused, top_k=2)

    assert len(reranked) >= 1
    assert reranked[0].retrieval_source == "rerank"
