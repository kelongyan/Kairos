"""RAG-specific schemas for retrieval traces and evidence packs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvidenceItemResponse(BaseModel):
    """A single evidence item used to answer a question."""

    doc_id: str
    chunk_id: str
    section: str = ""
    page_start: int
    page_end: int
    chunk_type: str = "paragraph"
    chunk_index: int = 0
    score: float
    retrieval_source: str = Field(
        ..., description="dense | sparse | fused | rerank"
    )
    text: str


class RetrievalHitResponse(BaseModel):
    """A retrieval hit surfaced in trace output."""

    doc_id: str
    chunk_id: str
    section: str = ""
    page_start: int
    page_end: int
    chunk_type: str = "paragraph"
    chunk_index: int = 0
    score: float
    retrieval_source: str = Field(
        ..., description="dense | sparse | fused | rerank"
    )
    text: str


class RetrievalTraceResponse(BaseModel):
    """Trace of the retrieval pipeline for a single question."""

    query: str
    rewritten_query: str
    dense_results: list[RetrievalHitResponse] = []
    sparse_results: list[RetrievalHitResponse] = []
    fused_results: list[RetrievalHitResponse] = []
    reranked_results: list[RetrievalHitResponse] = []
    evidence_pack: list[EvidenceItemResponse] = []


class AnswerArtifactsResponse(BaseModel):
    """Structured retrieval artifacts returned with a chat answer."""

    trace: RetrievalTraceResponse
