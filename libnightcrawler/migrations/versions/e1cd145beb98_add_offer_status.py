"""Add offer status

Revision ID: e1cd145beb98
Revises: 3c6b2423368c
Create Date: 2024-11-08 10:33:51.877702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from libnightcrawler.db.schema import Offer


# revision identifiers, used by Alembic.
revision: str = 'e1cd145beb98'
down_revision: Union[str, None] = '3c6b2423368c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    status = sa.Enum(Offer.OfferStatus, name="offerstatus")
    status.create(op.get_bind(), checkfirst=True)

    op.add_column("offers", sa.Column("status", sa.Enum(Offer.OfferStatus), nullable=False, default='UNPROCESSED', server_default='UNPROCESSED'))


def downgrade() -> None:
    pass
