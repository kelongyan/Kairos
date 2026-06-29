"""Question log and answer feedback ORM models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class QuestionLog(Base):
    """A persisted question and its answer."""

    __tablename__ = "question_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    question_log_id: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, default=_uuid
    )
    doc_id: Mapped[str | None] = mapped_column(
        String(128),
        ForeignKey("documents.doc_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    knowledge_base_id: Mapped[str | None] = mapped_column(
        String(128),
        ForeignKey("knowledge_bases.knowledge_base_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    question: Mapped[str] = mapped_column(Text, default="")
    answer: Mapped[str] = mapped_column(Text, default="")
    answer_status: Mapped[str] = mapped_column(String(32), default="answered", index=True)
    citations_json: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class AnswerFeedback(Base):
    """Minimal answer feedback for a question log."""

    __tablename__ = "answer_feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    feedback_id: Mapped[str] = mapped_column(String(128), unique=True, index=True, default=_uuid)
    question_log_id: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("question_logs.question_log_id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    useful: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    citation_accurate: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
