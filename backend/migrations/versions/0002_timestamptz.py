"""use timestamptz for user and status timestamps

Revision ID: 0002_timestamptz
Revises: 0001_initial
Create Date: 2026-02-04

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_timestamptz"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "created_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        nullable=False,
    )
    op.alter_column(
        "item_status",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        existing_type=sa.DateTime(),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "item_status",
        "updated_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "users",
        "created_at",
        type_=sa.DateTime(),
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
