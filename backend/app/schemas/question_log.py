"""Question log and feedback schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QuestionLogCreateRequest(BaseModel):
    """A question log creation payload."""

    doc_id: str | None = None
    knowledge_base_id: str | None = None
    question: str = Field(..., min_length=1)
    answer: str = ""
    answer_status: str = "answered"
    citations_json: list[dict[str, object]] = Field(default_factory=list)


class QuestionLogResponse(BaseModel):
    """Public question log representation."""

    model_config = ConfigDict(from_attributes=True)

    question_log_id: str
    doc_id: str | None
    knowledge_base_id: str | None
    question: str
    answer: str
    answer_status: str
    citations_json: list[dict[str, object]]
    created_at: datetime
    updated_at: datetime


class AnswerFeedbackRequest(BaseModel):
    """Minimal answer feedback payload."""

    useful: bool | None = None
    citation_accurate: bool | None = None


class AnswerFeedbackResponse(BaseModel):
    """Public answer feedback representation."""

    model_config = ConfigDict(from_attributes=True)

    feedback_id: str
    question_log_id: str
    useful: bool | None
    citation_accurate: bool | None
    created_at: datetime
    updated_at: datetime


class QuestionLogListResponse(BaseModel):
    """List of question logs."""

    question_logs: list[QuestionLogResponse]
