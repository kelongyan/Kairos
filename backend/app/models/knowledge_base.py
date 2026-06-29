"""Knowledge base ORM model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.document import Document


def _uuid() -> str:
    return str(uuid.uuid4())


class KnowledgeBase(Base):
    """A knowledge base containing owned documents."""

    __tablename__ = "knowledge_bases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    knowledge_base_id: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, default=_uuid
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    owner_id: Mapped[str] = mapped_column(String(128), default="")
    visibility: Mapped[str] = mapped_column(String(32), default="private")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    documents: Mapped[list[Document]] = relationship(
        back_populates="knowledge_base", cascade="all, delete-orphan"
    )
