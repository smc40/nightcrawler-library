"""Organizations mgmt

Revision ID: d74433221f34
Revises: fc3f4975e260
Create Date: 2024-11-22 10:14:04.593678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd74433221f34'
down_revision: Union[str, None] = 'fc3f4975e260'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("organizations", "countries")
    op.drop_column("organizations", "languages")
    op.drop_column("organizations", "currencies")

    op.drop_column("users", "org_id")
    op.alter_column("users", "role", server_default='USER')

    op.create_table(
        "user_organizations",
        sa.Column(
            "user_id",
            sa.String(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True,
        ),
        sa.Column(
            "org_id",
            sa.Integer(),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
            primary_key=True,
        )
    )

    op.add_column("keywords", sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
    op.execute("update keywords set updated_at=created_at")



def downgrade() -> None:
    pass
