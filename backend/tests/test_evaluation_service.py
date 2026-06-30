"""Tests for the repeatable evaluation service."""

from __future__ import annotations

from datetime import UTC, datetime

from app.services import evaluation_service


def test_phase2_eval_question_set_is_repeatable() -> None:
    questions = evaluation_service.load_phase2_eval_questions()

    assert len(questions) >= 3
    assert questions[0]["question"]
    assert "expected_keywords" in questions[0]


def test_list_datasets_seeds_default_dataset(monkeypatch) -> None:
    class FakeDataset:
        dataset_key = "phase2_fixed_qa"
        name = "Phase 2 fixed QA set"
        description = "Repeatable evaluation set"
        source_uri = "tests/fixtures/phase2_eval_questions.csv"
        questions_json = [{"sequence": 1, "question": "Q", "expected_keywords": ["a"]}]
        created_at = datetime(2026, 6, 30, tzinfo=UTC)
        updated_at = datetime(2026, 6, 30, tzinfo=UTC)

    monkeypatch.setattr(
        evaluation_service.evaluation_repo, "list_datasets", lambda db: [FakeDataset()]
    )
    monkeypatch.setattr(evaluation_service, "_ensure_phase2_dataset", lambda db: FakeDataset())

    datasets = evaluation_service.list_datasets(object())

    assert datasets[0].dataset_key == "phase2_fixed_qa"
    assert datasets[0].question_count == 1


def test_get_dataset_detail_returns_questions(monkeypatch) -> None:
    class FakeDataset:
        dataset_key = "phase2_fixed_qa"
        name = "Phase 2 fixed QA set"
        description = "Repeatable evaluation set"
        source_uri = "tests/fixtures/phase2_eval_questions.csv"
        questions_json = [
            {"sequence": 1, "question": "Q", "expected_keywords": ["a"], "notes": "note"}
        ]
        created_at = datetime(2026, 6, 30, tzinfo=UTC)
        updated_at = datetime(2026, 6, 30, tzinfo=UTC)

    monkeypatch.setattr(evaluation_service, "_ensure_phase2_dataset", lambda db: FakeDataset())
    monkeypatch.setattr(
        evaluation_service.evaluation_repo, "get_dataset", lambda db, key: FakeDataset()
    )

    dataset = evaluation_service.get_dataset_detail(object(), "phase2_fixed_qa")

    assert dataset is not None
    assert dataset.questions[0].question == "Q"
