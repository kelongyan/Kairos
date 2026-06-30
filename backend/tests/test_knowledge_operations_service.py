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
