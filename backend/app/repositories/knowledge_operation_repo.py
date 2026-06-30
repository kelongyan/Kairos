"""Knowledge operation item repository."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import KnowledgeOperationItem


def create_item(db: Session, item: KnowledgeOperationItem) -> KnowledgeOperationItem:
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_item(db: Session, item_id: str) -> KnowledgeOperationItem | None:
    return db.scalar(
        select(KnowledgeOperationItem).where(
            KnowledgeOperationItem.item_id == item_id
        )
    )


def get_item_by_source(
    db: Session,
    *,
    source_type: str,
    source_id: str,
    suggestion_type: str,
) -> KnowledgeOperationItem | None:
    return db.scalar(
        select(KnowledgeOperationItem).where(
            KnowledgeOperationItem.source_type == source_type,
            KnowledgeOperationItem.source_id == source_id,
            KnowledgeOperationItem.suggestion_type == suggestion_type,
        )
    )


def list_items(
    db: Session,
    *,
    knowledge_base_id: str | None = None,
    status: str | None = None,
) -> list[KnowledgeOperationItem]:
    query = select(KnowledgeOperationItem)
    if knowledge_base_id:
        query = query.where(KnowledgeOperationItem.knowledge_base_id == knowledge_base_id)
    if status:
        query = query.where(KnowledgeOperationItem.status == status)
    return list(
        db.scalars(
            query.order_by(
                KnowledgeOperationItem.status.asc(),
                KnowledgeOperationItem.severity.desc(),
                KnowledgeOperationItem.created_at.desc(),
            )
        )
    )


def update_item(
    db: Session,
    item: KnowledgeOperationItem,
    *,
    status: str | None = None,
    resolution_note: str | None = None,
) -> KnowledgeOperationItem:
    if status is not None:
        item.status = status
    if resolution_note is not None:
        item.resolution_note = resolution_note
    db.commit()
    db.refresh(item)
    return item
