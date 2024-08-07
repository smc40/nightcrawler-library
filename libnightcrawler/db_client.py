import logging
import alembic.config


class DBClient():
    def __init__(self, settings):
        logging.warning("Initializing new DB client")
        self.settings = settings
        self.migrate()

    def migrate(self):
        logging.warning("Starting db migration")
        # Call to alembic changes the log level, so we backup and restore it
        previous_level = logging.getLogger().level
        alembic.config.main(argv=["--raiseerr", "upgrade", "head"])
        logging.getLogger().setLevel(previous_level)

    def list_cases(self):
        logging.warning("Listing cases")
        return []
