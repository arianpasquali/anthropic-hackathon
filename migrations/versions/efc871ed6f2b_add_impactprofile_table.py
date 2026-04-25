"""add_impactprofile_table

Revision ID: efc871ed6f2b
Revises: 9c7a6d6d7c54
Create Date: 2026-04-25 23:37:18.008168

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'efc871ed6f2b'
down_revision: Union[str, Sequence[str], None] = '9c7a6d6d7c54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'impactprofile',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('co2_weight', sa.Float(), nullable=False),
        sa.Column('social_weight', sa.Float(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('impactprofile', schema=None) as batch_op:
        batch_op.create_index('ix_impactprofile_key', ['key'], unique=True)


def downgrade() -> None:
    op.drop_table('impactprofile')
