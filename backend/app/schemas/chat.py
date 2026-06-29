"""Chat request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from app.schemas.rag import RetrievalTraceResponse


class ChatRequest(BaseModel):
    """A question about a document or knowledge base."""

    doc_id: str | None = Field(
        default=None, description="The document to query against."
    )
    knowledge_base_id: str | None = Field(
        default=None, description="The knowledge base to query against."
    )
    question: str = Field(..., min_length=1, description="The user's question.")

    @model_validator(mode="after")
    def validate_scope(self) -> ChatRequest:
        if not self.doc_id and not self.knowledge_base_id:
            msg = "Either doc_id or knowledge_base_id is required."
            raise ValueError(msg)
        return self


class CitationResponse(BaseModel):
    """A citation supporting an answer."""

    doc_id: str
    chunk_id: str
    section: str = ""
    page: int
    quote: str
    score: float


class ChatResponse(BaseModel):
    """The answer plus supporting citations."""

    answer: str
    citations: list[CitationResponse]
    trace: RetrievalTraceResponse | None = None
    question_log_id: str | None = None
