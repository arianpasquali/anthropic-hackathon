"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-25
"""

from __future__ import annotations

from alembic import op

from app.core.database import Base
import app.models  # noqa: F401 — register tables on Base.metadata

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables defined on Base.metadata.

    The plan describes a Postgres schema with GEOGRAPHY, GENERATED columns,
    and triggers. Those are all wired in follow-up migrations; the initial
    revision creates the column-level shape that the ORM owns.
    """
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
