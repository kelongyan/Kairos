"""Tests for persisted knowledge operation items."""

from __future__ import annotations

from datetime import UTC, datetime

from app.services import knowledge_operations_service


class _QuestionLog:
    question_log_id = "ql-1"
    doc_id = "doc-1"
    knowledge_base_id = "kb-1"
    question = "How do we handle incident escalation?"
    answer_status = "insufficient_evidence"
    created_at = datetime(2026, 6, 30, tzinfo=UTC)


class _AnsweredQuestionLog:
    question_log_id = "ql-2"
    doc_id = "doc-2"
    knowledge_base_id = "kb-1"
    question = "What is the owner assignment policy?"
    answer_status = "answered"
    created_at = datetime(2026, 6, 30, tzinfo=UTC)


class _Feedback:
    feedback_id = "fb-1"
    question_log_id = "ql-2"
    useful = False
    citation_accurate = False
    created_at = datetime(2026, 6, 30, tzinfo=UTC)


class _FailedDocument:
    doc_id = "doc-3"
    knowledge_base_id = "kb-1"
    title = "Broken source"
    status = "failed"
    error_message = "parse error"
    updated_at = datetime(2026, 6, 30, tzinfo=UTC)


class _AgentRun:
    run_id = "run-1"
    doc_id = "doc-1"
    knowledge_base_id = "kb-1"
    question_log_id = "ql-1"
    question = "Compare the risks and recommend the next operational steps."
    route = "multi_agent"
    status = "completed"
    answer_status = "answered"
    answer = "Answer"
    citations_json = []
    trace_json = {}
    total_latency_ms = 123


class _ReviewerStep:
    agent_name = "reviewer_agent"

    def __init__(self, *, review_status: str = "warning", unsupported_citation_count: int = 2):
        self.output_json = {
            "review_status": review_status,
            "unsupported_citation_count": unsupported_citation_count,
        }


class _PlainStep:
    agent_name = "writer_agent"
    output_json = {}


def test_list_items_syncs_generated_operations(monkeypatch) -> None:
    from app.repositories import (
        document_repo,
        knowledge_operation_repo,
        question_log_repo,
    )

    created = []

    def fake_create_item(db, item):
        item.created_at = datetime(2026, 6, 30, tzinfo=UTC)
        item.updated_at = datetime(2026, 6, 30, tzinfo=UTC)
        created.append(item)
        return item

    monkeypatch.setattr(
        question_log_repo,
        "list_question_logs",
        lambda db: [_QuestionLog(), _AnsweredQuestionLog()],
    )
    monkeypatch.setattr(question_log_repo, "list_answer_feedback", lambda db: [_Feedback()])
    monkeypatch.setattr(document_repo, "list_documents", lambda db: [_FailedDocument()])
    monkeypatch.setattr(
        knowledge_operation_repo,
        "get_item_by_source",
        lambda db, **kwargs: None,
    )
    monkeypatch.setattr(knowledge_operation_repo, "create_item", fake_create_item)
    monkeypatch.setattr(
        knowledge_operation_repo,
        "list_items",
        lambda db, **kwargs: created,
    )

    items = knowledge_operations_service.list_items(object(), knowledge_base_id="kb-1")

    assert {item.suggestion_type for item in items} == {
        "faq_draft",
        "answer_quality_review",
        "reindex_document",
    }
    assert all(item.status == "pending" for item in items)


def test_list_items_does_not_duplicate_existing_operations(monkeypatch) -> None:
    from app.repositories import (
        document_repo,
        knowledge_operation_repo,
        question_log_repo,
    )

    monkeypatch.setattr(question_log_repo, "list_question_logs", lambda db: [_QuestionLog()])
    monkeypatch.setattr(question_log_repo, "list_answer_feedback", lambda db: [])
    monkeypatch.setattr(document_repo, "list_documents", lambda db: [])
    monkeypatch.setattr(
        knowledge_operation_repo,
        "get_item_by_source",
        lambda db, **kwargs: object(),
    )
    monkeypatch.setattr(
        knowledge_operation_repo,
        "create_item",
        lambda db, item: (_ for _ in ()).throw(AssertionError("unexpected create")),
    )
    monkeypatch.setattr(knowledge_operation_repo, "list_items", lambda db, **kwargs: [])

    items = knowledge_operations_service.list_items(object(), knowledge_base_id="kb-1")

    assert items == []


def test_sync_agent_run_item_creates_review_item(monkeypatch) -> None:
    from app.repositories import agent_run_repo, knowledge_operation_repo

    created = []

    def fake_create_item(db, item):
        created.append(item)
        return item

    monkeypatch.setattr(agent_run_repo, "get_agent_run", lambda db, run_id: _AgentRun())
    monkeypatch.setattr(
        agent_run_repo,
        "list_agent_steps",
        lambda db, run_id: [_PlainStep(), _ReviewerStep()],
    )
    monkeypatch.setattr(
        knowledge_operation_repo,
        "get_item_by_source",
        lambda db, **kwargs: None,
    )
    monkeypatch.setattr(knowledge_operation_repo, "create_item", fake_create_item)

    item = knowledge_operations_service.sync_agent_run_item(object(), run_id="run-1")

    assert item is not None
    assert item.source_type == "agent_run"
    assert item.source_id == "run-1"
    assert item.agent_run_id == "run-1"
    assert item.suggestion_type == "agent_review"
    assert item.title == "Review Agent citation warning"
    assert created[0].agent_run_id == "run-1"


def test_sync_agent_run_item_reuses_existing_review_item(monkeypatch) -> None:
    from app.repositories import agent_run_repo, knowledge_operation_repo

    existing = object()

    monkeypatch.setattr(agent_run_repo, "get_agent_run", lambda db, run_id: _AgentRun())
    monkeypatch.setattr(
        agent_run_repo,
        "list_agent_steps",
        lambda db, run_id: [_ReviewerStep(review_status="warning", unsupported_citation_count=1)],
    )
    monkeypatch.setattr(
        knowledge_operation_repo,
        "get_item_by_source",
        lambda db, **kwargs: existing,
    )
    monkeypatch.setattr(
        knowledge_operation_repo,
        "create_item",
        lambda db, item: (_ for _ in ()).throw(AssertionError("unexpected create")),
    )

    item = knowledge_operations_service.sync_agent_run_item(object(), run_id="run-1")

    assert item is existing


def test_list_items_filters_by_source_type_and_source_id(monkeypatch) -> None:
    from app.repositories import (
        agent_run_repo,
        document_repo,
        knowledge_operation_repo,
        question_log_repo,
    )

    captured = {}

    monkeypatch.setattr(question_log_repo, "list_question_logs", lambda db: [])
    monkeypatch.setattr(question_log_repo, "list_answer_feedback", lambda db: [])
    monkeypatch.setattr(document_repo, "list_documents", lambda db: [])
    monkeypatch.setattr(agent_run_repo, "list_agent_runs", lambda db, **kwargs: [])
    monkeypatch.setattr(agent_run_repo, "list_agent_steps", lambda db, run_id: [])
    monkeypatch.setattr(
        knowledge_operation_repo,
        "list_items",
        lambda db, **kwargs: captured.update(kwargs) or [],
    )
    monkeypatch.setattr(
        knowledge_operation_repo,
        "get_item_by_source",
        lambda db, **kwargs: object(),
    )

    items = knowledge_operations_service.list_items(
        object(),
        knowledge_base_id="kb-1",
        status="pending",
        source_type="agent_run",
        source_id="run-1",
    )

    assert items == []
    assert captured == {
        "knowledge_base_id": "kb-1",
        "status": "pending",
        "source_type": "agent_run",
        "source_id": "run-1",
    }
