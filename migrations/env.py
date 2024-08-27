from logging.config import fileConfig

from sqlalchemy import create_engine

from alembic import context

from libnightcrawler.settings import PostgresSettings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

settings = PostgresSettings()

# 'sqlalchemy.url' option is set during integration tests
url = config.get_main_option('sqlalchemy.url')
engine = create_engine(url) if url else create_engine(settings.connection_string)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()
