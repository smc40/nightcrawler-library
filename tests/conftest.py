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
