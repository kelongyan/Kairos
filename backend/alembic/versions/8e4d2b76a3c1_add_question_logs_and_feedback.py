"""add question logs and feedback

Revision ID: 8e4d2b76a3c1
Revises: 55c2f9f5e8b1
Create Date: 2026-06-30 08:30:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8e4d2b76a3c1"
down_revision: str | Sequence[str] | None = "55c2f9f5e8b1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "question_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("question_log_id", sa.String(length=128), nullable=False),
        sa.Column("doc_id", sa.String(length=128), nullable=True),
        sa.Column("knowledge_base_id", sa.String(length=128), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("answer_status", sa.String(length=32), nullable=False),
        sa.Column("citations_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["doc_id"], ["documents.doc_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id"], ["knowledge_bases.knowledge_base_id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_log_id"),
    )
    op.create_index(
        "ix_question_logs_question_log_id",
        "question_logs",
        ["question_log_id"],
        unique=True,
    )
    op.create_index("ix_question_logs_doc_id", "question_logs", ["doc_id"], unique=False)
    op.create_index(
        "ix_question_logs_knowledge_base_id",
        "question_logs",
        ["knowledge_base_id"],
        unique=False,
    )
    op.create_index(
        "ix_question_logs_answer_status",
        "question_logs",
        ["answer_status"],
        unique=False,
    )

    op.create_table(
        "answer_feedback",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("feedback_id", sa.String(length=128), nullable=False),
        sa.Column("question_log_id", sa.String(length=128), nullable=False),
        sa.Column("useful", sa.Boolean(), nullable=True),
        sa.Column("citation_accurate", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["question_log_id"], ["question_logs.question_log_id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("feedback_id"),
        sa.UniqueConstraint("question_log_id"),
    )
    op.create_index(
        "ix_answer_feedback_feedback_id",
        "answer_feedback",
        ["feedback_id"],
        unique=True,
    )
    op.create_index(
        "ix_answer_feedback_question_log_id",
        "answer_feedback",
        ["question_log_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_answer_feedback_question_log_id", table_name="answer_feedback")
    op.drop_index("ix_answer_feedback_feedback_id", table_name="answer_feedback")
    op.drop_table("answer_feedback")

    op.drop_index("ix_question_logs_answer_status", table_name="question_logs")
    op.drop_index("ix_question_logs_knowledge_base_id", table_name="question_logs")
    op.drop_index("ix_question_logs_doc_id", table_name="question_logs")
    op.drop_index("ix_question_logs_question_log_id", table_name="question_logs")
    op.drop_table("question_logs")
