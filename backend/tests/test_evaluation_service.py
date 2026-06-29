"""Tests for the fixed Phase 2 evaluation question set."""

from __future__ import annotations

from app.services.evaluation_service import load_phase2_eval_questions


def test_phase2_eval_question_set_is_repeatable() -> None:
    questions = load_phase2_eval_questions()

    assert len(questions) >= 3
    assert questions[0]["question"]
    assert "expected_keywords" in questions[0]
