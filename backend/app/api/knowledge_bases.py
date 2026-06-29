"""Knowledge base API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.knowledge_base import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseListResponse,
    KnowledgeBaseResponse,
    KnowledgeBaseUpdateRequest,
)
from app.services import knowledge_base_service

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


@router.post("", response_model=KnowledgeBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_knowledge_base(
    request: KnowledgeBaseCreateRequest,
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    kb = knowledge_base_service.create_knowledge_base(
        db,
        name=request.name,
        description=request.description,
        status=request.status,
        owner_id=request.owner_id,
        visibility=request.visibility,
    )
    return KnowledgeBaseResponse.model_validate(kb)


@router.get("", response_model=KnowledgeBaseListResponse)
async def list_knowledge_bases(db: Session = Depends(get_db)) -> KnowledgeBaseListResponse:
    bases = knowledge_base_service.list_knowledge_bases(db)
    return KnowledgeBaseListResponse(
        knowledge_bases=[KnowledgeBaseResponse.model_validate(kb) for kb in bases]
    )


@router.get("/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(
    knowledge_base_id: str,
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    kb = knowledge_base_service.get_knowledge_base(db, knowledge_base_id)
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base not found: {knowledge_base_id}",
        )
    return KnowledgeBaseResponse.model_validate(kb)


@router.patch("/{knowledge_base_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(
    knowledge_base_id: str,
    request: KnowledgeBaseUpdateRequest,
    db: Session = Depends(get_db),
) -> KnowledgeBaseResponse:
    kb = knowledge_base_service.update_knowledge_base(
        db,
        knowledge_base_id,
        name=request.name,
        description=request.description,
        status=request.status,
        owner_id=request.owner_id,
        visibility=request.visibility,
    )
    if kb is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge base not found: {knowledge_base_id}",
        )
    return KnowledgeBaseResponse.model_validate(kb)
