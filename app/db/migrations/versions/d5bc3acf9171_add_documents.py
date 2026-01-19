"""add documents

Revision ID: d5bc3acf9171
Revises: edc44e479611
Create Date: 2026-01-19 18:59:42.428276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d5bc3acf9171"
down_revision: Union[str, Sequence[str], None] = "edc44e479611"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- invites.token sicher hinzufügen ---
    # 1) Spalte nullable + Default
    op.add_column(
        "invites",
        sa.Column(
            "token",
            sa.String(length=255),
            nullable=True,
            server_default="",
        ),
    )

    # 2) Bestehende Rows absichern
    op.execute("UPDATE invites SET token = '' WHERE token IS NULL")

    # 3) Default entfernen + NOT NULL setzen
    op.alter_column(
        "invites",
        "token",
        server_default=None,
        nullable=False,
    )

    # Optional aber sinnvoll
    op.create_index(
        op.f("ix_invites_token"),
        "invites",
        ["token"],
        unique=True,
    )

    # --- documents Tabelle ---
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("scope", sa.String(length=20), nullable=False),
        sa.Column("property_id", sa.Integer(), nullable=True),
        sa.Column("unit_id", sa.Integer(), nullable=True),
        sa.Column("uploaded_by", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("minio_key", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"]),
        sa.ForeignKeyConstraint(["unit_id"], ["units.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_documents_minio_key"),
        "documents",
        ["minio_key"],
        unique=True,
    )
    op.create_index(
        op.f("ix_documents_tenant_id"),
        "documents",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_scope"),
        "documents",
        ["scope"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_property_id"),
        "documents",
        ["property_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_documents_unit_id"),
        "documents",
        ["unit_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_documents_unit_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_property_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_scope"), table_name="documents")
    op.drop_index(op.f("ix_documents_tenant_id"), table_name="documents")
    op.drop_index(op.f("ix_documents_minio_key"), table_name="documents")
    op.drop_table("documents")

    op.drop_index(op.f("ix_invites_token"), table_name="invites")
    op.drop_column("invites", "token")
