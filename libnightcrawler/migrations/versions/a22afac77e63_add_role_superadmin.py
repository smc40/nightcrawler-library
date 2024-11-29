"""Add role superadmin

Revision ID: a22afac77e63
Revises: d74433221f34
Create Date: 2024-11-27 13:37:13.887849

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a22afac77e63'
down_revision: Union[str, None] = 'd74433221f34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE roles ADD VALUE if not exists 'SUPERADMIN'")
    op.execute("ALTER TYPE offerstatus ADD VALUE if not exists 'FILTERED'")
    op.execute("ALTER TYPE offerstatus ADD VALUE if not exists 'ERROR'")


def downgrade() -> None:
    pass
