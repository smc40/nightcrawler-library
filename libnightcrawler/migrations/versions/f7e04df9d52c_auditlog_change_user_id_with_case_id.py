"""Auditlog change user_id with case_id

Revision ID: f7e04df9d52c
Revises: 9d154cc2d43b
Create Date: 2024-11-01 15:29:33.397262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7e04df9d52c'
down_revision: Union[str, None] = '9d154cc2d43b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("audit_logs", "user_id")
    op.add_column("audit_logs", sa.Column("case_id", sa.Integer(), nullable=False, default=0, index=True))


def downgrade() -> None:
    pass
