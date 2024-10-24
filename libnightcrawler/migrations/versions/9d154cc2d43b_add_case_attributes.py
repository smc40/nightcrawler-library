"""Add case attributes

Revision ID: 9d154cc2d43b
Revises: b4bb088ddce4
Create Date: 2024-10-21 18:27:57.064111

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d154cc2d43b"
down_revision: Union[str, None] = "b4bb088ddce4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("cases", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column("cases", sa.Column("end_date", sa.Date(), nullable=True))
    op.add_column("cases", sa.Column("repeat", sa.String(), nullable=False, default="daily", server_default="daily"))
    pass


def downgrade() -> None:
    pass
