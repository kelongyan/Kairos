"""add knowledge operation items

Revision ID: a1d2e3f4b5c6
Revises: 9b7a6c3d2e1f
Create Date: 2026-06-30 13:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1d2e3f4b5c6"
down_revision: str | Sequence[str] | None = "9b7a6c3d2e1f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "knowledge_operation_items",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("item_id", sa.String(length=128), nullable=False),
        sa.Column("knowledge_base_id", sa.String(length=128), nullable=True),
        sa.Column("doc_id", sa.String(length=128), nullable=True),
        sa.Column("question_log_id", sa.String(length=128), nullable=True),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=128), nullable=False),
        sa.Column("suggestion_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("suggested_action", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("resolution_note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["doc_id"], ["documents.doc_id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["knowledge_base_id"],
            ["knowledge_bases.knowledge_base_id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["question_log_id"], ["question_logs.question_log_id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("item_id"),
    )
    op.create_index(
        "ix_knowledge_operation_items_item_id",
        "knowledge_operation_items",
        ["item_id"],
        unique=True,
    )
    op.create_index(
        "ix_knowledge_operation_items_knowledge_base_id",
        "knowledge_operation_items",
        ["knowledge_base_id"],
        unique=False,
    )
    op.create_index(
        "ix_knowledge_operation_items_doc_id",
        "knowledge_operation_items",
        ["doc_id"],
        unique=False,
    )
    op.create_index(
        "ix_knowledge_operation_items_question_log_id",
        "knowledge_operation_items",
        ["question_log_id"],
        unique=False,
    )
    op.create_index(
        "ix_knowledge_operation_items_source_type",
        "knowledge_operation_items",
        ["source_type"],
        unique=False,
    )
    op.create_index(
        "ix_knowledge_operation_items_source_id",
        "knowledge_operation_items",
        ["source_id"],
        unique=False,
    )
    op.create_index(
        "ix_knowledge_operation_items_suggestion_type",
        "knowledge_operation_items",
        ["suggestion_type"],
        unique=False,
    )
    op.create_index(
        "ix_knowledge_operation_items_severity",
        "knowledge_operation_items",
        ["severity"],
        unique=False,
    )
    op.create_index(
        "ix_knowledge_operation_items_status",
        "knowledge_operation_items",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_operation_items_status", table_name="knowledge_operation_items")
    op.drop_index("ix_knowledge_operation_items_severity", table_name="knowledge_operation_items")
    op.drop_index(
        "ix_knowledge_operation_items_suggestion_type",
        table_name="knowledge_operation_items",
    )
    op.drop_index("ix_knowledge_operation_items_source_id", table_name="knowledge_operation_items")
    op.drop_index(
        "ix_knowledge_operation_items_source_type",
        table_name="knowledge_operation_items",
    )
    op.drop_index(
        "ix_knowledge_operation_items_question_log_id",
        table_name="knowledge_operation_items",
    )
    op.drop_index("ix_knowledge_operation_items_doc_id", table_name="knowledge_operation_items")
    op.drop_index(
        "ix_knowledge_operation_items_knowledge_base_id",
        table_name="knowledge_operation_items",
    )
    op.drop_index("ix_knowledge_operation_items_item_id", table_name="knowledge_operation_items")
    op.drop_table("knowledge_operation_items")
