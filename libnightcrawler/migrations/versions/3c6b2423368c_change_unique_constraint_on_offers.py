"""Change unique constraint on offers

Revision ID: 3c6b2423368c
Revises: f7e04df9d52c
Create Date: 2024-11-04 11:58:37.211225

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from libnightcrawler.db.schema import Offer
import libnightcrawler.utils as lu
import logging


# revision identifiers, used by Alembic.
revision: str = '3c6b2423368c'
down_revision: Union[str, None] = 'f7e04df9d52c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind, autoflush=False)

    op.drop_constraint("uq_offers_url_case_id", "offers")
    #op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    # This fails with error: "STABLE functions used in UPDATE queries cannot be called with column references"
    #op.execute("update offers set uid=encode(digest(concat(split_part(url, '?', 1), title), 'sha256'), 'hex')")
    op.execute("update offers set uid=url")
    op.create_unique_constraint("uq_offers_uid_case_id", "offers", columns=["uid", "case_id"])

    # Failure workaround: iterate over each offer individually
    seen = set()
    to_delete = list()
    to_save = list()
    offers = session.query(Offer).options(sa.orm.defer(Offer.status)).all()
    for offer in offers:
        offer.uid = lu.checksum(f"{offer.url.split('?')[0]}_{offer.title}")
        if offer.uid in seen:
            to_delete.append(offer.id)
            continue
        seen.add(offer.uid)
        to_save.append(offer)
    logging.warning("Will delete %d offers and keep %d", len(to_delete), len(to_save))
    stmt = sa.delete(Offer).where(Offer.id.in_(list(to_delete)))
    session.execute(stmt)
    if to_save:
        session.bulk_save_objects(to_save)
    session.commit()


def downgrade() -> None:
    pass
