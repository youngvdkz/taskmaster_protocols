"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-03

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("tg_id", sa.BigInteger(), primary_key=True),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "protocols",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.tg_id"]),
    )
    op.create_index("ix_protocols_user_id", "protocols", ["user_id"], unique=False)

    op.create_table(
        "items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("protocol_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["protocol_id"], ["protocols.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_items_protocol_id", "items", ["protocol_id"], unique=False)

    op.create_table(
        "item_status",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("protocol_id", sa.Integer(), nullable=False),
        sa.Column("item_id", sa.Integer(), nullable=False),
        sa.Column("checked", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.tg_id"]),
        sa.ForeignKeyConstraint(["protocol_id"], ["protocols.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "protocol_id", "item_id"),
        sa.UniqueConstraint("user_id", "protocol_id", "item_id", name="uq_item_status"),
    )


def downgrade() -> None:
    op.drop_table("item_status")
    op.drop_index("ix_items_protocol_id", table_name="items")
    op.drop_table("items")
    op.drop_index("ix_protocols_user_id", table_name="protocols")
    op.drop_table("protocols")
    op.drop_table("users")
