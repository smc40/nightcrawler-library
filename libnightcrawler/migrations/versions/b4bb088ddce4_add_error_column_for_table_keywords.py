"""Add error column for table keywords

Revision ID: b4bb088ddce4
Revises: 586bed9f19c2
Create Date: 2024-10-21 15:02:30.013358

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b4bb088ddce4"
down_revision: Union[str, None] = "586bed9f19c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("keywords", sa.Column("error", sa.String(), nullable=True))


def downgrade() -> None:
    pass
