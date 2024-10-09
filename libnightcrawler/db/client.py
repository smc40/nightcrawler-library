import logging
import alembic.config
import importlib.resources
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DBClient:
    def __init__(self, settings):
        logging.warning("Initializing new DB client")
        self.settings = settings
        self.migrate()
        self._session_factory = None

    @property
    def session_factory(self):
        if self._session_factory is None:
            engine = create_engine(self.settings.connection_string)
            self._session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return self._session_factory

    def migrate(self):
        logging.warning("Starting db migration")
        # Call to alembic changes the log level, so we backup and restore it
        previous_level = logging.getLogger().level
        with importlib.resources.as_file(importlib.resources.files("libnightcrawler").joinpath("alembic.ini")) as path:
            alembic.config.main(argv=["--raiseerr", "--config", str(path), "upgrade", "head"])
        logging.getLogger().setLevel(previous_level)
