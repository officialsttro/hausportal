"""add document object_key

Revision ID: 2bc7c66de307
Revises: d5bc3acf9171
Create Date: 2026-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2bc7c66de307"
down_revision: Union[str, Sequence[str], None] = "d5bc3acf9171"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) erst nullable anlegen, sonst knallt es bei bestehenden rows
    op.add_column("documents", sa.Column("object_key", sa.String(length=1024), nullable=True))
    op.create_index(op.f("ix_documents_object_key"), "documents", ["object_key"], unique=False)

    # 2) bestehende rows backfillen (für dein Test-Setup reicht ein stabiler Dummy)
    #    Upload ab jetzt speichert den echten Key sowieso.
    op.execute("UPDATE documents SET object_key = 'legacy/' || id::text WHERE object_key IS NULL")

    # 3) jetzt NOT NULL erzwingen
    op.alter_column("documents", "object_key", nullable=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_documents_object_key"), table_name="documents")
    op.drop_column("documents", "object_key")
