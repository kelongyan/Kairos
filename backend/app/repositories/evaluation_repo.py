"""Evaluation dataset and run repository."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import EvaluationDataset, EvaluationRun, EvaluationRunItem


def create_dataset(db: Session, dataset: EvaluationDataset) -> EvaluationDataset:
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    return dataset


def get_dataset(db: Session, dataset_key: str) -> EvaluationDataset | None:
    return db.get(EvaluationDataset, dataset_key)


def list_datasets(db: Session) -> list[EvaluationDataset]:
    return list(
        db.scalars(select(EvaluationDataset).order_by(EvaluationDataset.dataset_key.asc()))
    )


def create_run(db: Session, run: EvaluationRun) -> EvaluationRun:
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def get_run(db: Session, run_id: str) -> EvaluationRun | None:
    return db.scalar(select(EvaluationRun).where(EvaluationRun.run_id == run_id))


def list_runs(
    db: Session,
    *,
    dataset_key: str | None = None,
    knowledge_base_id: str | None = None,
    doc_id: str | None = None,
    execution_mode: str | None = None,
    status: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> list[EvaluationRun]:
    query = select(EvaluationRun)
    if dataset_key:
        query = query.where(EvaluationRun.dataset_key == dataset_key)
    if knowledge_base_id:
        query = query.where(EvaluationRun.knowledge_base_id == knowledge_base_id)
    if doc_id:
        query = query.where(EvaluationRun.doc_id == doc_id)
    if execution_mode:
        query = query.where(EvaluationRun.execution_mode == execution_mode)
    if status:
        query = query.where(EvaluationRun.status == status)
    if created_from:
        query = query.where(EvaluationRun.created_at >= created_from)
    if created_to:
        query = query.where(EvaluationRun.created_at <= created_to)
    return list(db.scalars(query.order_by(EvaluationRun.created_at.desc())))


def update_run(
    db: Session,
    run: EvaluationRun,
    *,
    status: str | None = None,
    question_count: int | None = None,
    passed_count: int | None = None,
    failed_count: int | None = None,
    average_latency_ms: int | None = None,
    summary_json: dict[str, object] | None = None,
) -> EvaluationRun:
    if status is not None:
        run.status = status
    if question_count is not None:
        run.question_count = question_count
    if passed_count is not None:
        run.passed_count = passed_count
    if failed_count is not None:
        run.failed_count = failed_count
    if average_latency_ms is not None:
        run.average_latency_ms = average_latency_ms
    if summary_json is not None:
        run.summary_json = summary_json
    db.commit()
    db.refresh(run)
    return run


def create_run_item(db: Session, item: EvaluationRunItem) -> EvaluationRunItem:
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_run_item(db: Session, item_id: str) -> EvaluationRunItem | None:
    return db.scalar(select(EvaluationRunItem).where(EvaluationRunItem.item_id == item_id))


def list_run_items(db: Session, run_id: str) -> list[EvaluationRunItem]:
    return list(
        db.scalars(
            select(EvaluationRunItem)
            .where(EvaluationRunItem.run_id == run_id)
            .order_by(EvaluationRunItem.sequence.asc())
        )
    )
