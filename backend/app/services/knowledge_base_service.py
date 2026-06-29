"""Knowledge base service."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models import KnowledgeBase
from app.repositories import knowledge_base_repo


def create_knowledge_base(
    db: Session,
    *,
    name: str,
    description: str = "",
    status: str = "active",
    owner_id: str = "",
    visibility: str = "private",
) -> KnowledgeBase:
    return knowledge_base_repo.create_knowledge_base(
        db,
        KnowledgeBase(
            knowledge_base_id=str(uuid.uuid4()),
            name=name,
            description=description,
            status=status,
            owner_id=owner_id,
            visibility=visibility,
        ),
    )


def get_knowledge_base(db: Session, knowledge_base_id: str) -> KnowledgeBase | None:
    return knowledge_base_repo.get_knowledge_base(db, knowledge_base_id)


def list_knowledge_bases(db: Session) -> list[KnowledgeBase]:
    return knowledge_base_repo.list_knowledge_bases(db)


def update_knowledge_base(
    db: Session,
    knowledge_base_id: str,
    *,
    name: str | None = None,
    description: str | None = None,
    status: str | None = None,
    owner_id: str | None = None,
    visibility: str | None = None,
) -> KnowledgeBase | None:
    kb = knowledge_base_repo.get_knowledge_base(db, knowledge_base_id)
    if kb is None:
        return None
    if name is not None:
        kb.name = name
    if description is not None:
        kb.description = description
    if status is not None:
        kb.status = status
    if owner_id is not None:
        kb.owner_id = owner_id
    if visibility is not None:
        kb.visibility = visibility
    db.commit()
    db.refresh(kb)
    return kb
