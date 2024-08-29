import logging
from libnightcrawler.settings import Settings
from libnightcrawler.db.client import DBClient
from libnightcrawler.db.schema import Cost, COST_UNIT_FACTOR
from sqlalchemy import func


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

    @property
    def db_session(self):
        return self.db_client.db_session

    # -------------------------------------
    # Object storage interface
    # -------------------------------------
    def _store_object(self, path: str, content: dict):
        logging.warning("Storing content to %s", path)
        # TODO

    def store_object(self, tenant_id: str, path: str, content: dict):
        return self._store_object(f"{tenant_id}/{path}", content)

    # -------------------------------------
    # Cost management
    # -------------------------------------
    def report_cost(self, case_id, cost, unit):
        logging.warning(f"{case_id}: Adding cost : {cost} {unit}")
        with self.db_client.session_factory() as session:
            session.add(Cost(
                case_id=case_id,
                value=cost,
                unit=unit))
            session.commit()

    def get_current_cost(self, case_id):
        totals = dict()
        # Get sum of costs group by unit
        with self.db_client.session_factory() as session:
            values = session.query(Cost.unit, func.sum(Cost.value)).where(Cost.case_id == case_id).group_by(Cost.unit).all()
            for (unit, value) in values:
                totals[unit] = totals.get(unit, 0) + value

        # Combine different units
        return sum([v*COST_UNIT_FACTOR[k] for k,v in totals.items()])
