"""Hybrid retrieval orchestration for Phase 2.

Combines deterministic query rewrite, dense retrieval, sparse retrieval, RRF
fusion, rerank, and evidence-pack assembly while preserving the Phase 1 dense
retriever as an independent boundary.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.providers import get_reranker_provider
from app.schemas.rag import (
    EvidenceItemResponse,
    RetrievalHitResponse,
    RetrievalTraceResponse,
)
from app.services.embedding_service import embed_query
from app.services.query_service import rewrite_query
from app.services.sparse_retrieval_service import retrieve_sparse
from app.services.vector_service import RetrievedChunk, retrieve


@dataclass
class RetrievedEvidence:
    """Retrieved chunk plus the stage that surfaced it."""

    chunk: RetrievedChunk
    retrieval_source: str


@dataclass
class RetrievalResult:
    """Structured result of the retrieval pipeline."""

    rewritten_query: str
    dense_results: list[RetrievedEvidence]
    sparse_results: list[RetrievedEvidence]
    fused_results: list[RetrievedEvidence]
    reranked_results: list[RetrievedEvidence]
    evidence_pack: list[RetrievedEvidence]

    def to_trace(self, query: str) -> RetrievalTraceResponse:
        return RetrievalTraceResponse(
            query=query,
            rewritten_query=self.rewritten_query,
            dense_results=[_to_trace_hit(item) for item in self.dense_results],
            sparse_results=[_to_trace_hit(item) for item in self.sparse_results],
            fused_results=[_to_trace_hit(item) for item in self.fused_results],
            reranked_results=[_to_trace_hit(item) for item in self.reranked_results],
            evidence_pack=[_to_evidence_item(item) for item in self.evidence_pack],
        )


def run_hybrid_retrieval(
    db: Session,
    *,
    doc_id: str | None = None,
    knowledge_base_id: str | None = None,
    question: str,
) -> RetrievalResult:
    """Run Phase 2 retrieval: rewrite -> dense+sparse -> RRF -> rerank -> evidence."""
    settings = get_settings()
    rewritten_query = rewrite_query(question)
    query_vector = embed_query(rewritten_query)

    dense = [
        RetrievedEvidence(chunk=chunk, retrieval_source="dense")
        for chunk in retrieve(
            query_vector,
            doc_id=doc_id,
            knowledge_base_id=knowledge_base_id,
            top_k=settings.retrieval_top_k,
        )
    ]
    sparse = [
        RetrievedEvidence(chunk=chunk, retrieval_source="sparse")
        for chunk in retrieve_sparse(
            db,
            rewritten_query,
            doc_id=doc_id,
            knowledge_base_id=knowledge_base_id,
            top_k=settings.sparse_retrieval_top_k,
        )
    ]

    fused = _rrf_fuse(
        dense,
        sparse,
        top_k=max(settings.retrieval_top_k, settings.sparse_retrieval_top_k),
    )
    reranked = _rerank(rewritten_query, fused, top_k=settings.rerank_top_k)
    evidence_pack = list(reranked)
    return RetrievalResult(
        rewritten_query=rewritten_query,
        dense_results=dense,
        sparse_results=sparse,
        fused_results=fused,
        reranked_results=reranked,
        evidence_pack=evidence_pack,
    )


def _rrf_fuse(
    dense_results: list[RetrievedEvidence],
    sparse_results: list[RetrievedEvidence],
    *,
    top_k: int,
    k: int = 60,
) -> list[RetrievedEvidence]:
    """Fuse ranked lists with Reciprocal Rank Fusion."""
    scores: dict[str, float] = {}
    chunks: dict[str, RetrievedChunk] = {}
    sources: dict[str, set[str]] = {}

    for results in (dense_results, sparse_results):
        for rank, item in enumerate(results, start=1):
            chunk_id = item.chunk.chunk_id
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
            chunks[chunk_id] = item.chunk
            sources.setdefault(chunk_id, set()).add(item.retrieval_source)

    ranked = sorted(scores.items(), key=lambda entry: entry[1], reverse=True)[:top_k]
    fused: list[RetrievedEvidence] = []
    for chunk_id, score in ranked:
        chunk = chunks[chunk_id]
        fused.append(
            RetrievedEvidence(
                chunk=RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    text=chunk.text,
                    section=chunk.section,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    chunk_type=chunk.chunk_type,
                    chunk_index=chunk.chunk_index,
                    score=score,
                ),
                retrieval_source=(
                    "dense+sparse"
                    if len(sources[chunk_id]) > 1
                    else next(iter(sources[chunk_id]))
                ),
            )
        )
    return fused


def _rerank(
    query: str,
    fused_results: list[RetrievedEvidence],
    *,
    top_k: int,
) -> list[RetrievedEvidence]:
    """Apply the configured reranker to fused candidates."""
    if not fused_results:
        return []

    reranker = get_reranker_provider()
    documents = [item.chunk.text for item in fused_results]
    ranked = reranker.rerank(query, documents, top_k=top_k)
    if not ranked:
        return fused_results[:top_k]

    reranked: list[RetrievedEvidence] = []
    for idx, score in ranked:
        item = fused_results[idx]
        chunk = item.chunk
        reranked.append(
            RetrievedEvidence(
                chunk=RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    text=chunk.text,
                    section=chunk.section,
                    page_start=chunk.page_start,
                    page_end=chunk.page_end,
                    chunk_type=chunk.chunk_type,
                    chunk_index=chunk.chunk_index,
                    score=score,
                ),
                retrieval_source="rerank",
            )
        )
    return reranked


def _to_trace_hit(item: RetrievedEvidence) -> RetrievalHitResponse:
    chunk = item.chunk
    return RetrievalHitResponse(
        doc_id=chunk.doc_id,
        chunk_id=chunk.chunk_id,
        section=chunk.section,
        page_start=chunk.page_start,
        page_end=chunk.page_end,
        chunk_type=chunk.chunk_type,
        chunk_index=chunk.chunk_index,
        score=chunk.score,
        retrieval_source=item.retrieval_source,
        text=chunk.text,
    )


def _to_evidence_item(item: RetrievedEvidence) -> EvidenceItemResponse:
    chunk = item.chunk
    return EvidenceItemResponse(
        doc_id=chunk.doc_id,
        chunk_id=chunk.chunk_id,
        section=chunk.section,
        page_start=chunk.page_start,
        page_end=chunk.page_end,
        chunk_type=chunk.chunk_type,
        chunk_index=chunk.chunk_index,
        score=chunk.score,
        retrieval_source=item.retrieval_source,
        text=chunk.text,
    )
