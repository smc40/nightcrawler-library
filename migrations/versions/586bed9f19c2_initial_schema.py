"""Initial schema

Revision ID: 586bed9f19c2
Revises: 
Create Date: 2024-08-27 12:57:58.900501

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm, text
from libnightcrawler.db.schema import FilterList, Tenant


# revision identifiers, used by Alembic.
revision: str = '586bed9f19c2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('countries', sa.String(), nullable=False),
        sa.Column('languages', sa.String(), nullable=False),
    )

    op.create_table(
        'filter_list',
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete="CASCADE"), nullable=False, index=True),
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
        sa.Column('tenant_id', sa.Integer(), nullable=False, index=True),
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


    # Insert first tenants
    tenants = [
        Tenant(id=1, name="Swissmedic", countries="ch", languages="de;fr;it;en"),
        Tenant(id=2, name="Ages", countries="at", languages="de;en")
    ]
    session.bulk_save_objects(tenants)

    # Insert blacklist
    items = ["20min.ch", "aargauerzeitung.ch", "admin.ch", "aids.ch", "avogel.ch", "bag.admin.ch", "beobachter.ch", "cash.ch", "cede.ch", "chartsurfer.de", "collinsdictionary.com", "compendium.ch", "de.langenscheidt.com", "dict.leo.org", "eldar.ch", "euniverse.ch", "euroclinix.net", "familienplanung.de", "fuw.ch", "g-ba.de", "has-sante.fr", "hitparade.ch", "infomedizin.ch", "jumbo.ch", "lilli.ch", "medix.ch", "music.apple.com", "mx3.ch", "nalda.ch", "netdoktor.ch", "nzz.ch", "oraletumortherapie.ch", "orellfuessli.ch", "pharmapro.ch", "pharmawiki.ch", "stitelecom.ch", "surfdome.com", "swissinfo.ch", "vertrauensaerzte.ch", "wirtschaftsregister.ch", "https://www.vergleich.org/", "https://www.unisante.ch/", "https://www.unicef.ch/", "https://www.swissuniversities.ch/", "https://geoscience-meeting.ch/", "https://www.pinterest.ch/", "https://www.logitech.com/", "https://www.salt.ch/", "https://www.vetpharm.uzh.ch/", "https://www.imm.uzh.ch/", "https://www.ksw.ch/", "https://www.eawag.ch", "https://www.salt.ch/", "https://dialysezentrum.ch/", "https://www.luzernerzeitung.ch/", "https://www.innosuisse.ch/", "https://www.bluewin.ch/", "https://www.thurgauerzeitung.ch/", "https://ch.kompass.com/", "https://www.letemps.ch/", "https://www.euroimmun.ch/", "https://quorus.ch/", "https://www.jobscout24.ch/", "https://ch.jooble.org/", "https://www.jobs.ch/", "https://www.local.ch/", "https://www.swissfirms.ch/", "https://business-monitor.ch/", "https://search.ch/", "https://fr.glassdoor.ch/", "https://www.ikea.com/", "https://www.nespresso.com/", "https://www.bookbeat.ch/", "https://boris.unibe.ch/", "https://ethz.ch/", "https://www.ige.ch/", "https://www.localcities.ch/", "https://ch.linkedin.com/", "https://www.nzz.ch/", "https://www.centerpassage.ch/", "https://www.vd.ch/", "https://www.tuugo.ch/", "https://www.rhyathlon.ch/", "https://www.suedostschweiz.ch/", "https://www.wwf.ch/", "http://www.parcs.ch/", "https://www.tripadvisor.ch/", "https://www.monetas.ch/", "https://www.business-informations.ch/", "https://ar.ch/", "https://www.epfl.ch/", "https://www.seismoverlag.ch/", "https://www.psi.ch/", "https://www.webwiki.ch/", "https://www.medizinonline.ch", "http://admin.ch", "http://Tagesanzeiger.ch", "https://medical-tribune.ch/", "https://www.allbiz.ch/", "http://nau.ch", "http://stadt-zuerich.ch", "http://h-fr.ch", "https://zlmsg.ch/", "http://usz.ch", "http://familienleben.ch", "http://symptome.ch", "http://wireltern.ch", "https://www.cscq.ch/", "http://kindgesund.ch", "http://nespresso.com", "http://swissmedicinfo.ch", "http://baby-und-kleinkind.ch", "http://20minuti.ch", "https://m4.ti.ch/", "http://hplus-bildung.ch", "http://familienleben.ch", "http://bewusstgesund.ch", "http://medix-ticino.ch", "http://pharmasuisse.org", "http://impuls.migros.ch", "http://mediaserver.unige.ch", "http://hplus-bildung.ch", "https://www.apodoc.ch/", "https://www.insel.ch/", "https://www.hug.ch/", "http://kayak.ch", "http://swoodoo.ch", "https://www.ksw.ch/", "http://www.pagesdor.ch/", "https://www.monetas.ch/", "https://tel.help.ch/", "https://www.webwiki.ch/", "https://www.rsi.ch/", "https://www.familienleben.ch/", "https://tesi.supsi.ch/", "https://de.glassdoor.ch/", "https://www.mediaplaner.ch/", "https://www.srf.ch/", "https://www.musiques-suisses.ch/", "https://edoc.unibas.ch/", "https://www.zora.uzh.ch/", "https://www.unispital-basel.ch/", "https://www.dcaf.ch/", "https://www.rf-partners.ch/", "https://www.eoc.ch/", "https://www.heckenpflanzendirekt.ch/", "https://www.lixt.ch/", "https://www.allbiz.ch/"]

    objects = [
        FilterList(
            tenant_id=1,
            name=x,
            url=x,
            type=FilterList.FilterListType.BLACKLIST,
            status=FilterList.FilterListStatus.ACTIVE,
            created_by='Auto')
        for x in items
    ]
    session.bulk_save_objects(objects)

    # Citus data
    session.execute(text("CREATE EXTENSION IF NOT EXISTS citus;"))
    session.execute(text("SELECT create_reference_table('tenants');"))
    session.execute(text("SELECT create_reference_table('filter_list');"))
    session.execute(text("SELECT create_distributed_table('cases', 'id');"))
    session.execute(text("SELECT create_distributed_table('case_members', 'case_id');"))
    session.execute(text("SELECT create_distributed_table('costs', 'case_id');"))
    session.commit()


def downgrade() -> None:
    pass
