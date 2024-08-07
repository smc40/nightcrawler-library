import logging
from libnightcrawler.settings import Settings
from libnightcrawler.db_client import DBClient


class Context:
    def __init__(self):
        logging.warning("Initializing new context")
        self.settings = Settings()
        self._pg_client = None

    @property
    def db_client(self):
        """ Lazy initialization of postgresql client """
        if self._pg_client is None:
            self._pg_client = DBClient(self.settings.postgres)
        return self._pg_client

    def _store_object(self, path: str, content: dict):
        logging.warning("Storing content to %s", path)
        # TODO

    def store_object(self, tenant_id: str, path: str, content: dict):
        return self._store_object(f"{tenant_id}/{path}", content)

    def report_cost(self, case_id, cost):
        logging.info("Adding cost to {case_id}: {cose}")
        # TODO
