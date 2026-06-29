"""Tests for question log and feedback API routes."""

from __future__ import annotations

from datetime import UTC

from fastapi.testclient import TestClient

from app.core.db import get_db
from app.main import app

client = TestClient(app)


class _FakeDB:
    def add(self, obj) -> None:
        self.obj = obj

    def commit(self) -> None:
        from datetime import datetime

        obj = getattr(self, "obj", None)
        if obj is None:
            return
        if not getattr(obj, "id", None):
            object.__setattr__(obj, "id", "fake-id")
        if getattr(obj, "created_at", None) is None:
            object.__setattr__(obj, "created_at", datetime.now(UTC))
        if getattr(obj, "updated_at", None) is None:
            object.__setattr__(obj, "updated_at", datetime.now(UTC))

    def refresh(self, obj) -> None:
        pass

    def close(self) -> None:
        pass


def _override_db(fake_db: _FakeDB) -> None:
    def _fake_get_db():
        yield fake_db

    app.dependency_overrides[get_db] = _fake_get_db


def _clear_override() -> None:
    app.dependency_overrides.pop(get_db, None)


def test_list_question_logs(monkeypatch) -> None:
    from app.services import question_log_service

    class FakeLog:
        question_log_id = "ql-1"
        doc_id = "doc-1"
        knowledge_base_id = "kb-1"
        question = "What is indexed?"
        answer = "The document is indexed."
        answer_status = "answered"
        citations_json = []
        created_at = "2026-06-30T00:00:00Z"
        updated_at = "2026-06-30T00:00:00Z"

    monkeypatch.setattr(question_log_service, "list_question_logs", lambda db: [FakeLog()])
    fake_db = _FakeDB()
    _override_db(fake_db)

    try:
        response = client.get("/question-logs")
    finally:
        _clear_override()

    assert response.status_code == 200
    body = response.json()
    assert len(body["question_logs"]) == 1
    assert body["question_logs"][0]["question_log_id"] == "ql-1"


def test_create_question_log(monkeypatch) -> None:
    from app.services import question_log_service

    class FakeLog:
        question_log_id = "ql-1"
        doc_id = "doc-1"
        knowledge_base_id = "kb-1"
        question = "What is indexed?"
        answer = "The document is indexed."
        answer_status = "answered"
        citations_json = []
        created_at = "2026-06-30T00:00:00Z"
        updated_at = "2026-06-30T00:00:00Z"

    monkeypatch.setattr(
        question_log_service,
        "create_question_log",
        lambda *args, **kwargs: FakeLog(),
    )
    fake_db = _FakeDB()
    _override_db(fake_db)

    try:
        response = client.post(
            "/question-logs",
            json={
                "doc_id": "doc-1",
                "knowledge_base_id": "kb-1",
                "question": "What is indexed?",
                "answer": "The document is indexed.",
                "answer_status": "answered",
                "citations_json": [],
            },
        )
    finally:
        _clear_override()

    assert response.status_code == 201
    assert response.json()["question_log_id"] == "ql-1"


def test_submit_feedback(monkeypatch) -> None:
    from app.services import question_log_service

    class FakeLog:
        question_log_id = "ql-1"

    class FakeFeedback:
        feedback_id = "fb-1"
        question_log_id = "ql-1"
        useful = True
        citation_accurate = False
        created_at = "2026-06-30T00:00:00Z"
        updated_at = "2026-06-30T00:00:00Z"

    monkeypatch.setattr(question_log_service, "get_question_log", lambda db, ql: FakeLog())
    monkeypatch.setattr(
        question_log_service,
        "create_or_update_feedback",
        lambda db, **kwargs: FakeFeedback(),
    )

    fake_db = _FakeDB()
    _override_db(fake_db)

    try:
        response = client.post(
            "/question-logs/ql-1/feedback",
            json={"useful": True, "citation_accurate": False},
        )
    finally:
        _clear_override()

    assert response.status_code == 200
    body = response.json()
    assert body["feedback_id"] == "fb-1"
    assert body["useful"] is True
