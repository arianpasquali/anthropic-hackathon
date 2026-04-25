"""add_missing_fields_to_ingestion_record

Revision ID: 9000c38b6fd1
Revises: fb55d1beb0e3
Create Date: 2026-04-25 21:19:16.758207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9000c38b6fd1'
down_revision: Union[str, Sequence[str], None] = 'fb55d1beb0e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('ingestionrecord', schema=None) as batch_op:
        batch_op.add_column(sa.Column('missing_fields', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('ingestionrecord', schema=None) as batch_op:
        batch_op.drop_column('missing_fields')
