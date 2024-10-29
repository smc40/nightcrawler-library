import logging
import alembic.config
import importlib.resources
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DBClient:
    def __init__(self, settings):
        logging.warning("Initializing new DB client")
        self.settings = settings
        self._session_factory = None
        if settings.auto_migrate:
            self.migrate()

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
        with importlib.resources.as_file(
            importlib.resources.files("libnightcrawler").joinpath("alembic.ini")
        ) as path:
            try:
                alembic.config.main(argv=["--raiseerr", "--config", str(path), "upgrade", "head"])
            except Exception as e:
                if self.settings.migration_failure_allowed:
                    logging.warning("Migration failed but allowed to fail in settings")
                    logging.info(e, exc_info=True)
                else:
                    raise e
        logging.getLogger().setLevel(previous_level)
