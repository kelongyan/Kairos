"""Tests for the hybrid retrieval service."""

from __future__ import annotations

from app.services.retrieval_service import RetrievalResult, RetrievedEvidence
from app.services.vector_service import RetrievedChunk


def test_retrieval_result_to_trace_serializes_all_sections() -> None:
    chunk = RetrievedChunk(
        chunk_id="chunk-1",
        doc_id="doc-1",
        text="Evidence text",
        section="Method",
        page_start=3,
        page_end=4,
        chunk_type="paragraph",
        chunk_index=0,
        score=0.9,
    )
    result = RetrievalResult(
        rewritten_query="rewritten",
        dense_results=[RetrievedEvidence(chunk=chunk, retrieval_source="dense")],
        sparse_results=[],
        fused_results=[RetrievedEvidence(chunk=chunk, retrieval_source="fused")],
        reranked_results=[RetrievedEvidence(chunk=chunk, retrieval_source="rerank")],
        evidence_pack=[RetrievedEvidence(chunk=chunk, retrieval_source="rerank")],
    )

    trace = result.to_trace("original")

    assert trace.query == "original"
    assert trace.rewritten_query == "rewritten"
    assert trace.dense_results[0].retrieval_source == "dense"
    assert trace.evidence_pack[0].retrieval_source == "rerank"
