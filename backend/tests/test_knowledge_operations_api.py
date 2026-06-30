"""Tests for knowledge operations API routes."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.core.db import get_db
from app.main import app

client = TestClient(app)


class _FakeItem:
    item_id = "item-1"
    knowledge_base_id = "kb-1"
    doc_id = "doc-1"
    question_log_id = "ql-1"
    source_type = "question_log"
    source_id = "ql-1"
    suggestion_type = "faq_draft"
    severity = "high"
    title = "Draft missing knowledge answer"
    description = "Missing evidence."
    suggested_action = "Create an FAQ draft."
    status = "pending"
    resolution_note = ""
    created_at = datetime(2026, 6, 30, tzinfo=UTC)
    updated_at = datetime(2026, 6, 30, tzinfo=UTC)


def _fake_get_db():
    yield object()


def test_list_knowledge_operation_items(monkeypatch) -> None:
    from app.services import knowledge_operations_service

    captured = {}

    def fake_list_items(
        db,
        *,
        knowledge_base_id=None,
        status=None,
        source_type=None,
        source_id=None,
    ):
        captured["knowledge_base_id"] = knowledge_base_id
        captured["status"] = status
        captured["source_type"] = source_type
        captured["source_id"] = source_id
        return [_FakeItem()]

    monkeypatch.setattr(knowledge_operations_service, "list_items", fake_list_items)

    app.dependency_overrides[get_db] = _fake_get_db
    try:
        response = client.get(
            "/knowledge-operations/items",
            params={
                "knowledge_base_id": "kb-1",
                "status": "pending",
                "source_type": "agent_run",
                "source_id": "run-1",
            },
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert captured == {
        "knowledge_base_id": "kb-1",
        "status": "pending",
        "source_type": "agent_run",
        "source_id": "run-1",
    }
    body = response.json()
    assert body["items"][0]["item_id"] == "item-1"
    assert body["items"][0]["status"] == "pending"


def test_update_knowledge_operation_item_status(monkeypatch) -> None:
    from app.services import knowledge_operations_service

    captured = {}

    class ResolvedItem(_FakeItem):
        status = "resolved"
        resolution_note = "Added missing FAQ."

    def fake_update_item(db, item_id, *, status, resolution_note):
        captured["item_id"] = item_id
        captured["status"] = status
        captured["resolution_note"] = resolution_note
        return ResolvedItem()

    monkeypatch.setattr(knowledge_operations_service, "update_item", fake_update_item)

    app.dependency_overrides[get_db] = _fake_get_db
    try:
        response = client.patch(
            "/knowledge-operations/items/item-1",
            json={"status": "resolved", "resolution_note": "Added missing FAQ."},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert captured == {
        "item_id": "item-1",
        "status": "resolved",
        "resolution_note": "Added missing FAQ.",
    }
    assert response.json()["status"] == "resolved"


def test_update_knowledge_operation_item_404(monkeypatch) -> None:
    from app.services import knowledge_operations_service

    monkeypatch.setattr(
        knowledge_operations_service,
        "update_item",
        lambda db, item_id, **kwargs: None,
    )

    app.dependency_overrides[get_db] = _fake_get_db
    try:
        response = client.patch(
            "/knowledge-operations/items/missing",
            json={"status": "ignored", "resolution_note": ""},
        )
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 404


def test_list_knowledge_operation_suggestions_uses_agent_run_items(monkeypatch) -> None:
    from app.api import knowledge_operations as knowledge_operations_api
    from app.services import knowledge_operations_service

    called = {}

    class FakeRun:
        knowledge_base_id = "kb-1"

    class Suggestion:
        suggestion_id = "item-1"
        item_id = "item-1"
        knowledge_base_id = "kb-1"
        doc_id = "doc-1"
        question_log_id = "ql-1"
        agent_run_id = "run-1"
        source_type = "agent_run"
        source_id = "run-1"
        suggestion_type = "agent_review"
        severity = "medium"
        title = "Review Agent run"
        description = "desc"
        suggested_action = "act"
        status = "pending"
        resolution_note = ""
        evidence = [{"source_type": "agent_run", "source_id": "run-1"}]
        created_at = datetime(2026, 6, 30, tzinfo=UTC)

    def fake_get_agent_run(db, run_id):
        called["agent_run_id"] = run_id
        return FakeRun()

    def fake_list_run_suggestions(db, *, run_id):
        called["run_id"] = run_id
        return [Suggestion()]

    monkeypatch.setattr(
        knowledge_operations_api.agent_run_repo,
        "get_agent_run",
        fake_get_agent_run,
    )
    monkeypatch.setattr(
        knowledge_operations_service,
        "list_run_suggestions",
        fake_list_run_suggestions,
    )

    app.dependency_overrides[get_db] = _fake_get_db
    try:
        response = client.get("/knowledge-operations/suggestions", params={"run_id": "run-1"})
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    assert called == {"agent_run_id": "run-1", "run_id": "run-1"}
    assert response.json()["suggestions"][0]["item_id"] == "item-1"
