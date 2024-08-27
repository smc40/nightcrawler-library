import os
from pprint import pprint

import pytest
import time
from alembicverify.util import (
    get_current_revision,
    get_head_revision,
    prepare_schema_from_migrations,
)
from sqlalchemydiff import compare
from sqlalchemydiff.util import (
    prepare_schema_from_models,
    get_temporary_uri,
)

from libnightcrawler.db.schema import Base


@pytest.fixture
def alembic_root() -> str:
    # make sure you run this test from the root directory of the backend-service sub-project
    return './migrations'


@pytest.fixture(scope="module")
def uri_left(db_uri):
    return get_temporary_uri(db_uri)


@pytest.fixture(scope="module")
def uri_right(db_uri):
    return get_temporary_uri(db_uri)


@pytest.mark.usefixtures("new_db_left")
def test_upgrade(uri_left, alembic_config_left):
    """Tests that we can apply all migrations from a brand new empty database."""
    engine, script = prepare_schema_from_migrations(uri_left, alembic_config_left)

    head = get_head_revision(alembic_config_left, engine, script)
    current = get_current_revision(alembic_config_left, engine, script)

    assert head == current


@pytest.mark.usefixtures("new_db_left")
@pytest.mark.usefixtures("new_db_right")
def test_model_and_migration_schemas_are_the_same(uri_left, uri_right, alembic_config_left):
    """Compare two databases.

    Compares the database obtained with all migrations against the
    one we get out of the models.
    """
    prepare_schema_from_migrations(uri_left, alembic_config_left)
    prepare_schema_from_models(uri_right, Base)

    result = compare(uri_left, uri_right, {'alembic_version'})

    if not result.is_match:
        pprint(result.errors)
    assert result.is_match
