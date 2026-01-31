"""add document publish fields

Revision ID: 3c8f0c2a1c2e
Revises: 2bc7c66de307
Create Date: 2026-01-31

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3c8f0c2a1c2e"
down_revision: Union[str, Sequence[str], None] = "2bc7c66de307"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("published_at", sa.DateTime(), nullable=True))
    op.add_column("documents", sa.Column("published_by", sa.Integer(), nullable=True))

    op.create_index(op.f("ix_documents_published_at"), "documents", ["published_at"], unique=False)
    op.create_index(op.f("ix_documents_published_by"), "documents", ["published_by"], unique=False)

    op.create_foreign_key(
        "documents_published_by_fkey",
        "documents",
        "users",
        ["published_by"],
        ["id"],
        ondelete=None,
    )


def downgrade() -> None:
    op.drop_constraint("documents_published_by_fkey", "documents", type_="foreignkey")
    op.drop_index(op.f("ix_documents_published_by"), table_name="documents")
    op.drop_index(op.f("ix_documents_published_at"), table_name="documents")

    op.drop_column("documents", "published_by")
    op.drop_column("documents", "published_at")
