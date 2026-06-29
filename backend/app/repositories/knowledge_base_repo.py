"""Knowledge base repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KnowledgeBase


def create_knowledge_base(db: Session, knowledge_base: KnowledgeBase) -> KnowledgeBase:
    db.add(knowledge_base)
    db.commit()
    db.refresh(knowledge_base)
    return knowledge_base


def get_knowledge_base(db: Session, knowledge_base_id: str) -> KnowledgeBase | None:
    return db.scalar(
        select(KnowledgeBase).where(KnowledgeBase.knowledge_base_id == knowledge_base_id)
    )


def get_knowledge_base_by_name(db: Session, name: str) -> KnowledgeBase | None:
    return db.scalar(select(KnowledgeBase).where(KnowledgeBase.name == name))


def list_knowledge_bases(db: Session) -> list[KnowledgeBase]:
    return list(
        db.scalars(select(KnowledgeBase).order_by(KnowledgeBase.created_at.desc()))
    )


def get_or_create_default_knowledge_base(db: Session) -> KnowledgeBase:
    knowledge_base = get_knowledge_base_by_name(db, "Default Knowledge Base")
    if knowledge_base is not None:
        return knowledge_base

    knowledge_base = KnowledgeBase(
        name="Default Knowledge Base",
        description="Fallback knowledge base for legacy single-document uploads.",
        status="active",
        owner_id="",
        visibility="private",
    )
    return create_knowledge_base(db, knowledge_base)
