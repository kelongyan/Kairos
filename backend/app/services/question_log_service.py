"""Question log and feedback service."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models import AnswerFeedback, QuestionLog
from app.repositories import question_log_repo


def create_question_log(
    db: Session,
    *,
    doc_id: str | None,
    knowledge_base_id: str | None,
    question: str,
    answer: str,
    answer_status: str,
    citations_json: list[dict[str, object]],
) -> QuestionLog:
    return question_log_repo.create_question_log(
        db,
        QuestionLog(
            question_log_id=str(uuid.uuid4()),
            doc_id=doc_id,
            knowledge_base_id=knowledge_base_id,
            question=question,
            answer=answer,
            answer_status=answer_status,
            citations_json=citations_json,
        ),
    )


def list_question_logs(db: Session) -> list[QuestionLog]:
    return question_log_repo.list_question_logs(db)


def get_question_log(db: Session, question_log_id: str) -> QuestionLog | None:
    return question_log_repo.get_question_log(db, question_log_id)


def create_or_update_feedback(
    db: Session,
    *,
    question_log_id: str,
    useful: bool | None = None,
    citation_accurate: bool | None = None,
) -> AnswerFeedback:
    feedback = question_log_repo.get_feedback_by_question_log(db, question_log_id)
    if feedback is None:
        feedback = AnswerFeedback(
            feedback_id=str(uuid.uuid4()),
            question_log_id=question_log_id,
            useful=useful,
            citation_accurate=citation_accurate,
        )
        return question_log_repo.create_answer_feedback(db, feedback)
    return question_log_repo.update_answer_feedback(
        db,
        feedback,
        useful=useful,
        citation_accurate=citation_accurate,
    )
