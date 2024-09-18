"""Initial schema

Revision ID: 586bed9f19c2
Revises: 
Create Date: 2024-08-27 12:57:58.900501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm, text, func
from libnightcrawler.db.schema import FilterList, Organization, Keyword, User


# revision identifiers, used by Alembic.
revision: str = '586bed9f19c2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('operation', sa.String(), nullable=False, index=True),
        sa.Column('payload', sa.JSON(), nullable=False),
    )

    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('countries', sa.String(), nullable=False),
        sa.Column('languages', sa.String(), nullable=False),
        sa.Column('currencies', sa.String(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
    )

    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False, primary_key=True),
        sa.Column('org_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete="CASCADE"), nullable=False, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('mail', sa.String(), nullable=False),
        sa.Column('role', sa.Enum(User.Roles), nullable=False),
    )

    op.create_table(
        'filter_list',
        sa.Column('org_id', sa.Integer(), sa.ForeignKey('organizations.id', ondelete="CASCADE"), nullable=False, index=True),
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('type', sa.Enum(FilterList.FilterListType), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('status', sa.Enum(FilterList.FilterListStatus), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("deleted_by", sa.String(), nullable=True),
    )

    op.create_table(
        'cases',
        sa.Column('org_id', sa.Integer(), nullable=False, index=True),
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, default='False'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('inactive', sa.Boolean(), nullable=False, default='False'),
        sa.Column('inactive_at', sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        'case_members',
        sa.Column('case_id', sa.Integer(), nullable=False, index=True, primary_key=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True, primary_key=True)
    )

    op.create_table(
        'costs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
        sa.Column('case_id', sa.Integer(), nullable=False, index=True, primary_key=True),
        sa.Column('value', sa.Integer(), nullable=False),
        sa.Column('unit', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'keywords',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True, index=True),
        sa.Column('case_id', sa.Integer(), nullable=False, index=True, primary_key=True),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False, default='False'),
        sa.Column('query', sa.String(), nullable=False),
        sa.Column('type', sa.Enum(Keyword.KeywordType), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('crawl_state', sa.Enum(Keyword.CrawlState), nullable=False),
    )

    op.create_index(index_name='uq_keywords_query_type_case_id', table_name='keywords',
                    columns=['query', 'type', 'case_id'], unique=True)

    op.create_table(
        'offers',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True, index=True),
        sa.Column('case_id', sa.Integer(), nullable=False, index=True, primary_key=True),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('relevant', sa.Boolean(), nullable=False, default=True),
        sa.Column('root', sa.String(), nullable=False),
        sa.Column('uid', sa.String(), nullable=False),
        sa.Column('platform', sa.String(), nullable=False),
        sa.Column('keyword_id', sa.Integer(), nullable=False, index=True),
        sa.Column('price', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('images', sa.JSON(), nullable=True),
        sa.Column('language', sa.String(), nullable=False),
        sa.Column('score', sa.Numeric(), nullable=False),
        sa.Column('crawled_at', sa.DateTime(timezone=True), nullable=False, server_default=func.now())
    )

    op.create_table('overall_bookmark',
        sa.Column('user_id', sa.String(), primary_key=True),
        sa.Column('offer_id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=func.now())
    )

    # Insert first organizations
    tenants = [
        Organization(id=1, name="Swissmedic MEP", countries="ch", currencies="CHF", languages="de;fr;it;en", unit="mep"),
        Organization(id=2, name="Swissmedic AM", countries="ch", currencies="CHF", languages="de;fr;it;en", unit="am"),
        Organization(id=3, name="Ages", countries="at", currencies="EURO", languages="de;en", unit="chocolatine")
    ]
    session.bulk_save_objects(tenants)

    # Insert blacklist
    items = ["20min.ch", "aargauerzeitung.ch", "admin.ch", "aids.ch", "avogel.ch", "bag.admin.ch", "beobachter.ch", "cash.ch", "cede.ch", "chartsurfer.de", "collinsdictionary.com", "compendium.ch", "de.langenscheidt.com", "dict.leo.org", "eldar.ch", "euniverse.ch", "euroclinix.net", "familienplanung.de", "fuw.ch", "g-ba.de", "has-sante.fr", "hitparade.ch", "infomedizin.ch", "jumbo.ch", "lilli.ch", "medix.ch", "music.apple.com", "mx3.ch", "nalda.ch", "netdoktor.ch", "nzz.ch", "oraletumortherapie.ch", "orellfuessli.ch", "pharmapro.ch", "pharmawiki.ch", "stitelecom.ch", "surfdome.com", "swissinfo.ch", "vertrauensaerzte.ch", "wirtschaftsregister.ch", "https://www.vergleich.org/", "https://www.unisante.ch/", "https://www.unicef.ch/", "https://www.swissuniversities.ch/", "https://geoscience-meeting.ch/", "https://www.pinterest.ch/", "https://www.logitech.com/", "https://www.salt.ch/", "https://www.vetpharm.uzh.ch/", "https://www.imm.uzh.ch/", "https://www.ksw.ch/", "https://www.eawag.ch", "https://www.salt.ch/", "https://dialysezentrum.ch/", "https://www.luzernerzeitung.ch/", "https://www.innosuisse.ch/", "https://www.bluewin.ch/", "https://www.thurgauerzeitung.ch/", "https://ch.kompass.com/", "https://www.letemps.ch/", "https://www.euroimmun.ch/", "https://quorus.ch/", "https://www.jobscout24.ch/", "https://ch.jooble.org/", "https://www.jobs.ch/", "https://www.local.ch/", "https://www.swissfirms.ch/", "https://business-monitor.ch/", "https://search.ch/", "https://fr.glassdoor.ch/", "https://www.ikea.com/", "https://www.nespresso.com/", "https://www.bookbeat.ch/", "https://boris.unibe.ch/", "https://ethz.ch/", "https://www.ige.ch/", "https://www.localcities.ch/", "https://ch.linkedin.com/", "https://www.nzz.ch/", "https://www.centerpassage.ch/", "https://www.vd.ch/", "https://www.tuugo.ch/", "https://www.rhyathlon.ch/", "https://www.suedostschweiz.ch/", "https://www.wwf.ch/", "http://www.parcs.ch/", "https://www.tripadvisor.ch/", "https://www.monetas.ch/", "https://www.business-informations.ch/", "https://ar.ch/", "https://www.epfl.ch/", "https://www.seismoverlag.ch/", "https://www.psi.ch/", "https://www.webwiki.ch/", "https://www.medizinonline.ch", "http://admin.ch", "http://Tagesanzeiger.ch", "https://medical-tribune.ch/", "https://www.allbiz.ch/", "http://nau.ch", "http://stadt-zuerich.ch", "http://h-fr.ch", "https://zlmsg.ch/", "http://usz.ch", "http://familienleben.ch", "http://symptome.ch", "http://wireltern.ch", "https://www.cscq.ch/", "http://kindgesund.ch", "http://nespresso.com", "http://swissmedicinfo.ch", "http://baby-und-kleinkind.ch", "http://20minuti.ch", "https://m4.ti.ch/", "http://hplus-bildung.ch", "http://familienleben.ch", "http://bewusstgesund.ch", "http://medix-ticino.ch", "http://pharmasuisse.org", "http://impuls.migros.ch", "http://mediaserver.unige.ch", "http://hplus-bildung.ch", "https://www.apodoc.ch/", "https://www.insel.ch/", "https://www.hug.ch/", "http://kayak.ch", "http://swoodoo.ch", "https://www.ksw.ch/", "http://www.pagesdor.ch/", "https://www.monetas.ch/", "https://tel.help.ch/", "https://www.webwiki.ch/", "https://www.rsi.ch/", "https://www.familienleben.ch/", "https://tesi.supsi.ch/", "https://de.glassdoor.ch/", "https://www.mediaplaner.ch/", "https://www.srf.ch/", "https://www.musiques-suisses.ch/", "https://edoc.unibas.ch/", "https://www.zora.uzh.ch/", "https://www.unispital-basel.ch/", "https://www.dcaf.ch/", "https://www.rf-partners.ch/", "https://www.eoc.ch/", "https://www.heckenpflanzendirekt.ch/", "https://www.lixt.ch/", "https://www.allbiz.ch/"]

    objects = [
        FilterList(
            org_id=y,
            name=x,
            url=x,
            type=FilterList.FilterListType.BLACKLIST,
            status=FilterList.FilterListStatus.ACTIVE,
            created_by='Auto')
        for x in items for y in [1, 2]
    ]
    session.bulk_save_objects(objects)

    # Citus data
    session.execute(text("CREATE EXTENSION IF NOT EXISTS citus;"))
    session.execute(text("SELECT create_reference_table('organizations');"))
    session.execute(text("SELECT create_reference_table('filter_list');"))
    session.execute(text("SELECT create_distributed_table('cases', 'id');"))
    session.execute(text("SELECT create_distributed_table('case_members', 'case_id');"))
    session.execute(text("SELECT create_distributed_table('keywords', 'case_id');"))
    session.execute(text("SELECT create_distributed_table('costs', 'case_id');"))
    session.execute(text("SELECT create_distributed_table('offers', 'case_id');"))
    session.commit()


def downgrade() -> None:
    pass
