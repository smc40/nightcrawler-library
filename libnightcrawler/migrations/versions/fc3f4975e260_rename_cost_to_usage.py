"""Rename cost to usage

Revision ID: fc3f4975e260
Revises: e1cd145beb98
Create Date: 2024-11-08 16:40:02.497275

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'fc3f4975e260'
down_revision: Union[str, None] = 'e1cd145beb98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('costs', 'usages')
    op.execute('ALTER SEQUENCE costs_id_seq RENAME TO usages_id_seq')
    op.execute('ALTER INDEX ix_costs_case_id RENAME TO ix_usages_case_id')
    op.execute('ALTER INDEX costs_pkey RENAME TO usages_pkey')


def downgrade() -> None:
    pass
