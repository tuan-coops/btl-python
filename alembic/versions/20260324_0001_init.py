"""Initial schema

Revision ID: 20260324_0001
Revises:
Create Date: 2026-03-24 16:05:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260324_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "health_check_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_health_check_logs_id"),
        "health_check_logs",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_health_check_logs_id"), table_name="health_check_logs")
    op.drop_table("health_check_logs")
