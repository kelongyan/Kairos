"""add evaluations

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-30 15:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: str | Sequence[str] | None = "b2c3d4e5f6a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "evaluation_datasets",
        sa.Column("dataset_key", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source_uri", sa.String(length=512), nullable=False),
        sa.Column("questions_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("dataset_key"),
    )
    op.create_index(
        "ix_evaluation_datasets_dataset_key",
        "evaluation_datasets",
        ["dataset_key"],
        unique=True,
    )

    op.create_table(
        "evaluation_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=128), nullable=False),
        sa.Column("dataset_key", sa.String(length=128), nullable=False),
        sa.Column("knowledge_base_id", sa.String(length=128), nullable=True),
        sa.Column("doc_id", sa.String(length=128), nullable=True),
        sa.Column("execution_mode", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("passed_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("average_latency_ms", sa.Integer(), nullable=False),
        sa.Column("summary_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["dataset_key"], ["evaluation_datasets.dataset_key"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["doc_id"], ["documents.doc_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id"], ["knowledge_bases.knowledge_base_id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id"),
    )
    op.create_index("ix_evaluation_runs_run_id", "evaluation_runs", ["run_id"], unique=True)
    op.create_index(
        "ix_evaluation_runs_dataset_key",
        "evaluation_runs",
        ["dataset_key"],
        unique=False,
    )
    op.create_index(
        "ix_evaluation_runs_knowledge_base_id",
        "evaluation_runs",
        ["knowledge_base_id"],
        unique=False,
    )
    op.create_index("ix_evaluation_runs_doc_id", "evaluation_runs", ["doc_id"], unique=False)
    op.create_index(
        "ix_evaluation_runs_execution_mode",
        "evaluation_runs",
        ["execution_mode"],
        unique=False,
    )
    op.create_index("ix_evaluation_runs_status", "evaluation_runs", ["status"], unique=False)
    op.create_index(
        "ix_evaluation_runs_created_at",
        "evaluation_runs",
        ["created_at"],
        unique=False,
    )

    op.create_table(
        "evaluation_run_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("item_id", sa.String(length=128), nullable=False),
        sa.Column("run_id", sa.String(length=128), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("expected_keywords_json", sa.JSON(), nullable=False),
        sa.Column("matched_keywords_json", sa.JSON(), nullable=False),
        sa.Column("missing_keywords_json", sa.JSON(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("answer_status", sa.String(length=32), nullable=False),
        sa.Column("execution_route", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=False),
        sa.Column("latency_ms", sa.Integer(), nullable=False),
        sa.Column("question_log_id", sa.String(length=128), nullable=True),
        sa.Column("chat_trace_id", sa.String(length=128), nullable=True),
        sa.Column("agent_run_id", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["agent_run_id"], ["agent_runs.run_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["chat_trace_id"], ["chat_traces.trace_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["question_log_id"], ["question_logs.question_log_id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["run_id"], ["evaluation_runs.run_id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id"),
    )
    op.create_index(
        "ix_evaluation_run_items_item_id",
        "evaluation_run_items",
        ["item_id"],
        unique=True,
    )
    op.create_index(
        "ix_evaluation_run_items_run_id",
        "evaluation_run_items",
        ["run_id"],
        unique=False,
    )
    op.create_index(
        "ix_evaluation_run_items_status",
        "evaluation_run_items",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_evaluation_run_items_question_log_id",
        "evaluation_run_items",
        ["question_log_id"],
        unique=False,
    )
    op.create_index(
        "ix_evaluation_run_items_chat_trace_id",
        "evaluation_run_items",
        ["chat_trace_id"],
        unique=False,
    )
    op.create_index(
        "ix_evaluation_run_items_agent_run_id",
        "evaluation_run_items",
        ["agent_run_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_evaluation_run_items_agent_run_id", table_name="evaluation_run_items")
    op.drop_index("ix_evaluation_run_items_chat_trace_id", table_name="evaluation_run_items")
    op.drop_index("ix_evaluation_run_items_question_log_id", table_name="evaluation_run_items")
    op.drop_index("ix_evaluation_run_items_status", table_name="evaluation_run_items")
    op.drop_index("ix_evaluation_run_items_run_id", table_name="evaluation_run_items")
    op.drop_index("ix_evaluation_run_items_item_id", table_name="evaluation_run_items")
    op.drop_table("evaluation_run_items")

    op.drop_index("ix_evaluation_runs_created_at", table_name="evaluation_runs")
    op.drop_index("ix_evaluation_runs_status", table_name="evaluation_runs")
    op.drop_index("ix_evaluation_runs_execution_mode", table_name="evaluation_runs")
    op.drop_index("ix_evaluation_runs_doc_id", table_name="evaluation_runs")
    op.drop_index("ix_evaluation_runs_knowledge_base_id", table_name="evaluation_runs")
    op.drop_index("ix_evaluation_runs_dataset_key", table_name="evaluation_runs")
    op.drop_index("ix_evaluation_runs_run_id", table_name="evaluation_runs")
    op.drop_table("evaluation_runs")

    op.drop_index("ix_evaluation_datasets_dataset_key", table_name="evaluation_datasets")
    op.drop_table("evaluation_datasets")
