import pytest
from libnightcrawler.context import Context


@pytest.fixture(scope='session')
def context():
    return Context()
