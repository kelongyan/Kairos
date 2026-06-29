"""add knowledge bases and document scope

Revision ID: 55c2f9f5e8b1
Revises: 7a6442d093d5
Create Date: 2026-06-29 22:00:00.000000

"""

from __future__ import annotations

import uuid
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "55c2f9f5e8b1"
down_revision: str | Sequence[str] | None = "7a6442d093d5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DEFAULT_KB_ID = str(uuid.uuid4())
DEFAULT_KB_NAME = "Default Knowledge Base"


def upgrade() -> None:
    connection = op.get_bind()

    op.create_table(
        "knowledge_bases",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("knowledge_base_id", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("owner_id", sa.String(length=128), nullable=False),
        sa.Column("visibility", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("knowledge_base_id"),
    )
    op.create_index(
        "ix_knowledge_bases_knowledge_base_id",
        "knowledge_bases",
        ["knowledge_base_id"],
        unique=True,
    )
    op.create_index("ix_knowledge_bases_status", "knowledge_bases", ["status"], unique=False)

    connection.execute(
        sa.text(
            """
            INSERT INTO knowledge_bases
                (id, knowledge_base_id, name, description, status, owner_id, visibility)
            VALUES
                (:id, :knowledge_base_id, :name, :description, :status, :owner_id, :visibility)
            """
        ),
        {
            "id": str(uuid.uuid4()),
            "knowledge_base_id": DEFAULT_KB_ID,
            "name": DEFAULT_KB_NAME,
            "description": "Fallback knowledge base for legacy single-document uploads.",
            "status": "active",
            "owner_id": "",
            "visibility": "private",
        },
    )

    op.add_column(
        "documents",
        sa.Column("knowledge_base_id", sa.String(length=128), nullable=True),
    )
    op.create_index(
        "ix_documents_knowledge_base_id",
        "documents",
        ["knowledge_base_id"],
        unique=False,
    )
    connection.execute(
        sa.text(
            "UPDATE documents SET knowledge_base_id = :knowledge_base_id "
            "WHERE knowledge_base_id IS NULL OR knowledge_base_id = ''"
        ),
        {"knowledge_base_id": DEFAULT_KB_ID},
    )
    op.alter_column("documents", "knowledge_base_id", nullable=False)
    op.create_foreign_key(
        "fk_documents_knowledge_base_id_knowledge_bases",
        "documents",
        "knowledge_bases",
        ["knowledge_base_id"],
        ["knowledge_base_id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_documents_knowledge_base_id_knowledge_bases",
        "documents",
        type_="foreignkey",
    )
    op.drop_index("ix_documents_knowledge_base_id", table_name="documents")
    op.drop_column("documents", "knowledge_base_id")

    op.drop_index("ix_knowledge_bases_status", table_name="knowledge_bases")
    op.drop_index("ix_knowledge_bases_knowledge_base_id", table_name="knowledge_bases")
    op.drop_table("knowledge_bases")
