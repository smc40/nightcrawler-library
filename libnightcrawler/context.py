import logging
import json
from libnightcrawler.settings import Settings
from libnightcrawler.db.client import DBClient
from libnightcrawler.blob import BlobClient
import libnightcrawler.db.schema as lds
import libnightcrawler.objects as lo
import libnightcrawler.utils as lu
from sqlalchemy import func
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert


class Context:
    def __init__(self):
        logging.warning("Initializing new context")
        self.settings = Settings()
        self._pg_client = None
        self._blob_client = None

    @property
    def db_client(self) -> DBClient:
        """Lazy initialization of postgresql client"""
        if self._pg_client is None:
            self._pg_client = DBClient(self.settings.postgres)
        return self._pg_client

    @property
    def blob_client(self) -> BlobClient:
        """Lazy initialization of blob client"""
        if self._blob_client is None:
            self._blob_client = BlobClient(self.settings.blob)
        return self._blob_client

    # -------------------------------------
    # Object storage interface
    # -------------------------------------
    def _store_object(self, path: str, content: dict):
        logging.warning("Storing content to %s", path)
        # TODO

    def store_object(self, org_id: str, path: str, content: dict):
        return self._store_object(f"{org_id}/{path}", content)

    # -------------------------------------
    # Cost management
    # -------------------------------------
    def report_cost(self, case_id: int, cost: int, unit: str):
        logging.warning(f"{case_id}: Adding cost : {cost} {unit}")
        with self.db_client.session_factory() as session:
            session.add(lds.Cost(case_id=case_id, value=cost, unit=unit))
            session.commit()

    def get_current_cost(self, case_id: int) -> float:
        totals = dict[str, int]()
        # Get sum of costs group by unit
        with self.db_client.session_factory() as session:
            values = (
                session.query(lds.Cost.unit, func.sum(lds.Cost.value))
                .where(lds.Cost.case_id == case_id)
                .group_by(lds.Cost.unit)
                .all()
            )
            for unit, value in values:
                totals[unit] = totals.get(unit, 0) + value

        # Combine different units
        return sum([v * lds.COST_UNIT_FACTOR[k] for k, v in totals.items()])

    # -------------------------------------
    # DS pipeline utils
    # -------------------------------------
    def get_organization(
        self, name: str | None = None, index_by_name: bool = True
    ) -> dict[str, lo.Organization]:
        logging.info("Fetching organizations")
        if self.settings.use_file_storage:
            if not index_by_name:
                raise ValueError("Data form local file storage does not have IDs")

            with open(self.settings.organizations_path, "r") as f:
                data = json.load(f)
                res = dict[str, lo.Organization]()
                for name, value in data.items():
                    if name is None:
                        continue
                    res[name] = lo.Organization(name=name, **value)
                return res

        with self.db_client.session_factory() as session:
            orgs = session.query(
                lds.Organization,
                sa.func.array_agg(
                    sa.func.json_build_array(lds.FilterList.url, lds.FilterList.type)
                ),
            ).outerjoin(
                lds.FilterList,
                lds.FilterList.org_id == lds.Organization.id
                and lds.FilterList.status == lds.FilterList.FilterListStatus.ACTIVE,
            )
            if name:
                orgs = orgs.where(lds.Organization.name == name)
            orgs = orgs.group_by(lds.Organization.id).all()
            if name:
                assert len(orgs) == 1

            res = dict()
            for org in orgs:
                key = org[0].name if index_by_name else org[0].id

                res[key] = lo.Organization(
                    name=org[0].name,
                    unit=org[0].unit,
                    countries=org[0].countries.split(";"),
                    currencies=org[0].currencies.split(";"),
                    languages=org[0].languages.split(";"),
                    blacklist=[
                        x[0] for x in org[1] if x[1] == lds.FilterList.FilterListType.BLACKLIST.name
                    ],
                )
            return res

    def get_crawl_requests(self) -> list[lo.CrawlRequest]:
        orgs = self.get_organization(index_by_name=False)
        with self.db_client.session_factory() as session:
            cases = (
                session.query(
                    lds.Case,
                    sa.func.array_agg(
                        sa.func.json_build_array(
                            lds.Keyword.query, lds.Keyword.type, lds.Keyword.id
                        )
                    ),
                )
                .join(lds.Keyword, lds.Keyword.case_id == lds.Case.id)
                .where(lds.Case.inactive == False)  # noqa
                .group_by(lds.Case.id)
                .all()
            )
        return [
            lo.CrawlRequest(
                keyword_type=y[1],
                keyword_value=y[0],
                organization=orgs[x[0].org_id],
                keyword_id=y[2],
                case_id=x[0].id,
            )
            for x in cases
            for y in x[1]
        ]

    def store_results(self, data: list[lo.CrawlResult]):
        logging.warning("Storing %d results", len(data))
        with self.db_client.session_factory() as session:
            for result in data:
                values = {
                    x: y for x, y in result.offer.to_dict().items() if x not in ["id", "crawled_at"]
                }
                images = []
                for image_url in result.images:
                    extension = lu.get_extension(image_url)
                    content = lu.get_content(image_url)
                    checksum = lu.checksum(content)
                    path = f"{result.request.organization.name}/{checksum}.{extension}"
                    self.blob_client.put_image(path, content)
                    images.append({"source": image_url, "path": path})
                values["images"] = images
                stmt = insert(lds.Offer).values(values)
                do_update_stmt = stmt.on_conflict_do_update(
                    constraint="uq_offers_url_case_id",
                    set_={x: getattr(stmt.excluded, x) for x in values},
                )
                session.execute(do_update_stmt)
            session.commit()
