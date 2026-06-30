"""Knowledge operations API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.knowledge_operations import (
    KnowledgeOperationItemListResponse,
    KnowledgeOperationItemResponse,
    KnowledgeOperationItemUpdateRequest,
    KnowledgeOperationSuggestionListResponse,
)
from app.services import knowledge_operations_service

router = APIRouter(prefix="/knowledge-operations", tags=["knowledge-operations"])


@router.get("/items", response_model=KnowledgeOperationItemListResponse)
async def list_items(
    knowledge_base_id: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
) -> KnowledgeOperationItemListResponse:
    """List persisted knowledge operation items."""
    items = knowledge_operations_service.list_items(
        db,
        knowledge_base_id=knowledge_base_id,
        status=status,
    )
    return KnowledgeOperationItemListResponse(
        items=[KnowledgeOperationItemResponse.model_validate(item) for item in items]
    )


@router.patch("/items/{item_id}", response_model=KnowledgeOperationItemResponse)
async def update_item(
    item_id: str,
    request: KnowledgeOperationItemUpdateRequest,
    db: Session = Depends(get_db),
) -> KnowledgeOperationItemResponse:
    """Update handling status for a knowledge operation item."""
    item = knowledge_operations_service.update_item(
        db,
        item_id,
        status=request.status,
        resolution_note=request.resolution_note,
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge operation item not found: {item_id}",
        )
    return KnowledgeOperationItemResponse.model_validate(item)


@router.get("/suggestions", response_model=KnowledgeOperationSuggestionListResponse)
async def list_suggestions(
    knowledge_base_id: str | None = None,
    db: Session = Depends(get_db),
) -> KnowledgeOperationSuggestionListResponse:
    """List generated knowledge operations suggestions."""
    suggestions = knowledge_operations_service.list_suggestions(
        db,
        knowledge_base_id=knowledge_base_id,
    )
    return KnowledgeOperationSuggestionListResponse(suggestions=suggestions)
