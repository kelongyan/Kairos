"""Schemas for knowledge operations suggestions."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

KnowledgeOperationStatus = Literal[
    "pending",
    "resolved",
    "ignored",
    "reindexed",
    "document_added",
]


class KnowledgeOperationItemResponse(BaseModel):
    """A persisted actionable item for improving a knowledge base."""

    model_config = ConfigDict(from_attributes=True)

    item_id: str
    knowledge_base_id: str | None = None
    doc_id: str | None = None
    question_log_id: str | None = None
    agent_run_id: str | None = None
    source_type: str
    source_id: str
    suggestion_type: str
    severity: str
    title: str
    description: str
    suggested_action: str
    status: str
    resolution_note: str = ""
    created_at: datetime
    updated_at: datetime


class KnowledgeOperationItemUpdateRequest(BaseModel):
    """Update payload for handling a knowledge operation item."""

    status: KnowledgeOperationStatus
    resolution_note: str = Field(default="", max_length=2000)


class KnowledgeOperationItemListResponse(BaseModel):
    """List of persisted knowledge operation items."""

    items: list[KnowledgeOperationItemResponse]


class KnowledgeOperationSuggestionResponse(BaseModel):
    """Backward-compatible generated suggestion representation."""

    model_config = ConfigDict(from_attributes=True)

    suggestion_id: str
    item_id: str
    knowledge_base_id: str | None = None
    doc_id: str | None = None
    question_log_id: str | None = None
    agent_run_id: str | None = None
    source_type: str
    source_id: str
    suggestion_type: str
    severity: str
    title: str
    description: str
    suggested_action: str
    status: str
    resolution_note: str = ""
    evidence: list[dict[str, object]] = Field(default_factory=list)
    created_at: datetime | None = None


class KnowledgeOperationSuggestionListResponse(BaseModel):
    """Backward-compatible list of knowledge operation suggestions."""

    suggestions: list[KnowledgeOperationSuggestionResponse]
