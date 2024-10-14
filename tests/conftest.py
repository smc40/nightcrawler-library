import pytest
from libnightcrawler.context import Context


@pytest.fixture(scope='session')
def context():
    return Context()


@pytest.fixture(scope='session')
def db_uri(context):
    return context.settings.postgres.connection_string


@pytest.fixture(scope='session')
def org_id():
    return 1

@pytest.fixture(scope='session')
def second_org_id():
    return 2

@pytest.fixture(scope='session')
def case_id():
    return 4567

@pytest.fixture(scope='session')
def public_image():
    return "https://www.swissmedic.ch/swissmedic/fr/_jcr_content/logo/image.imagespooler.png/1672565955358/swissmedic-logo_transp.png"
