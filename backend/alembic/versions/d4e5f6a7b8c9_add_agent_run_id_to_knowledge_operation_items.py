"""add agent run id to knowledge operation items

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-30 16:30:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: str | Sequence[str] | None = "c3d4e5f6a7b8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "knowledge_operation_items",
        sa.Column("agent_run_id", sa.String(length=128), nullable=True),
    )
    op.create_foreign_key(
        "fk_knowledge_operation_items_agent_run_id_agent_runs",
        "knowledge_operation_items",
        "agent_runs",
        ["agent_run_id"],
        ["run_id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_knowledge_operation_items_agent_run_id",
        "knowledge_operation_items",
        ["agent_run_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_knowledge_operation_items_agent_run_id",
        table_name="knowledge_operation_items",
    )
    op.drop_constraint(
        "fk_knowledge_operation_items_agent_run_id_agent_runs",
        "knowledge_operation_items",
        type_="foreignkey",
    )
    op.drop_column("knowledge_operation_items", "agent_run_id")
