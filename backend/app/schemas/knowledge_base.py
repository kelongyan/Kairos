"""Knowledge base schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBaseBase(BaseModel):
    """Shared knowledge base fields."""

    name: str = Field(..., min_length=1, max_length=256)
    description: str = ""
    status: str = "active"
    owner_id: str = ""
    visibility: str = "private"


class KnowledgeBaseCreateRequest(KnowledgeBaseBase):
    """Knowledge base creation payload."""


class KnowledgeBaseUpdateRequest(BaseModel):
    """Knowledge base update payload."""

    name: str | None = Field(default=None, min_length=1, max_length=256)
    description: str | None = None
    status: str | None = None
    owner_id: str | None = None
    visibility: str | None = None


class KnowledgeBaseResponse(KnowledgeBaseBase):
    """Public representation of a knowledge base."""

    model_config = ConfigDict(from_attributes=True)

    knowledge_base_id: str
    created_at: datetime
    updated_at: datetime


class KnowledgeBaseListResponse(BaseModel):
    """List of knowledge bases."""

    knowledge_bases: list[KnowledgeBaseResponse]
