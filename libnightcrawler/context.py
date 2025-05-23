from datetime import datetime, timezone, timedelta
import logging
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
    # Report audit
    # -------------------------------------
    def add_audit_log(self, case_id: int, operation: str, payload: dict):
        logging.warning(f"{case_id}: Adding to audit log: {operation}")
        logging.info(payload)
        with self.db_client.session_factory() as session:
            session.add(lds.AuditLog(case_id=case_id, operation=operation, payload=payload))
            session.commit()

    # -------------------------------------
    # Usage management
    # -------------------------------------
    def report_usage(self, case_id: int, usages: dict[str, int]):
        logging.warning(f"{case_id}: Adding usage : {usages}")
        with self.db_client.session_factory() as session:
            for k, v in usages.items():
                if not v:
                    continue
                session.add(lds.Usage(case_id=case_id, value=v, unit=k))
            session.commit()

    def get_current_usage(self, case_id: int) -> float:
        totals = dict[str, int]()
        # Get sum of usages group by unit
        with self.db_client.session_factory() as session:
            values = (
                session.query(lds.Usage.unit, func.sum(lds.Usage.value))
                .where(lds.Usage.case_id == case_id)
                .group_by(lds.Usage.unit)
                .all()
            )
            for unit, value in values:
                totals[unit] = totals.get(unit, 0) + value

        # Combine different units
        return sum([v * lds.USAGE_UNIT_FACTOR[k] for k, v in totals.items()])

    # -------------------------------------
    # DS pipeline utils
    # -------------------------------------
    def get_organization(
        self, name: str | None = None, index_by_name: bool = True
    ) -> dict[str, lo.Organization]:
        logging.info("Fetching organizations")
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
                    blacklist=[
                        x[0] for x in org[1] if x[1] == lds.FilterList.FilterListType.BLACKLIST.name
                    ],
                    whitelist=[
                        x[0] for x in org[1] if x[1] == lds.FilterList.FilterListType.WHITELIST.name
                    ],
                )
            return res

    def get_crawl_requests(self, case_id: int = 0, keyword_id: int = 0) -> list[lo.CrawlRequest]:
        orgs = self.get_organization(index_by_name=False)
        with self.db_client.session_factory() as session:
            cases = session.query(
                lds.Case,
                sa.func.array_agg(
                    sa.func.json_build_array(lds.Keyword.query, lds.Keyword.type, lds.Keyword.id)
                ),
            ).join(lds.Keyword, lds.Keyword.case_id == lds.Case.id)
            if case_id:
                cases = cases.where(lds.Case.id == case_id)
            if keyword_id:
                cases = cases.where(lds.Keyword.id == keyword_id)
            if (not case_id) and (not keyword_id):
                today = datetime.now().date()
                cases = cases.where(
                    sa.and_(
                        lds.Case.inactive == False,  # noqa
                        sa.or_(lds.Case.end_date == None, lds.Case.end_date >= today),  # noqa
                    )
                )
            cases = cases.group_by(lds.Case.id).all()
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

    def set_crawl_pending(self, case_id: int, keyword_id: int):
        logging.warning("Change crawl state to pending for case %s keyword %s", case_id, keyword_id)
        with self.db_client.session_factory() as session:
            stmt = (
                sa.update(lds.Keyword)
                .where(lds.Keyword.id == keyword_id)
                .values(
                    crawl_state=lds.Keyword.CrawlState.PENDING,
                    updated_at=datetime.now(timezone.utc),
                )
            )
            session.execute(stmt)
            session.add(
                lds.AuditLog(
                    case_id=case_id,
                    operation="change_keyword_state",
                    payload={
                        "keyword_id": keyword_id,
                        "status": lds.Keyword.CrawlState.PENDING.name,
                    },
                )
            )
            session.commit()

    def set_crawl_error(self, case_id: int, keyword_id: int, error: str):
        logging.error("Crawl error for case %s keyword %s : %s", case_id, keyword_id, error)
        with self.db_client.session_factory() as session:
            stmt = (
                sa.update(lds.Keyword)
                .where(lds.Keyword.id == keyword_id)
                .values(
                    crawl_state=lds.Keyword.CrawlState.FAILED,
                    error=error,
                    updated_at=datetime.now(timezone.utc),
                )
            )
            session.execute(stmt)
            session.add(
                lds.AuditLog(
                    case_id=case_id,
                    operation="change_keyword_state",
                    payload={
                        "keyword_id": keyword_id,
                        "status": lds.Keyword.CrawlState.FAILED.name,
                    },
                )
            )
            session.commit()

    def store_results(
        self,
        data: list[lo.CrawlResult],
        case_id: int,
        keyword_id: int | None = None,
        status: lds.Keyword.CrawlState = lds.Keyword.CrawlState.SUCCEEDED,
    ):
        logging.warning("Storing %d results", len(data))
        with self.db_client.session_factory() as session:
            for result in data:
                values = {
                    x: y
                    for x, y in result.offer.to_dict().items()
                    if x not in ["id", "crawled_at", "status"]
                }
                images = []
                for image_url in result.images:
                    checksum = lu.checksum(image_url)
                    path = f"{result.request.organization.name}/{checksum}"
                    try:
                        if self.blob_client.image_exists(path):
                            # If already exists in storage, no need to re-download it
                            images.append({"source": image_url, "path": path})
                            continue
                        content, content_type = lu.get_content(image_url)
                    except Exception as e:
                        logging.error("failed to download image from %s: %s", image_url, str(e))
                        continue
                    self.blob_client.put_image(path, content, content_type)
                    images.append({"source": image_url, "path": path})
                values["images"] = images
                stmt = insert(lds.Offer).values(values)
                do_update_stmt = stmt.on_conflict_do_update(
                    constraint="uq_offers_uid_case_id",
                    set_={x: getattr(stmt.excluded, x) for x in values},
                )
                session.execute(do_update_stmt)
            if keyword_id:
                statement = (
                    sa.update(lds.Keyword)
                    .where(lds.Keyword.id == keyword_id)
                    .values(crawl_state=status, updated_at=datetime.now(timezone.utc))
                )
                session.execute(statement)
            session.add(
                lds.AuditLog(
                    created_at=datetime.now(timezone.utc),
                    case_id=case_id,
                    operation="change_keyword_state",
                    payload={"keyword_id": keyword_id, "status": status.name, "offers": len(data)},
                )
            )
            session.commit()

    # -------------------------------------
    # Daily schedule helpers
    # -------------------------------------
    def disable_expired_cases(self):
        logging.warning("Disabling expired cases")
        with self.db_client.session_factory() as session:
            session.execute(sa.text("update cases set inactive=True, inactive_at=now() where inactive=False and end_date < CURRENT_DATE"))
            session.commit()

    def get_today_keywords(self) -> list[int]:
        def get_threshold(repeat):
            if repeat == "daily":
                return timedelta(seconds=0)
            elif repeat == "weekly":
                return timedelta(days=7)
            elif repeat == "monthly":
                return timedelta(days=30)
            raise ValueError("Unknown repeat : %s", repeat)
        logging.info("Getting today's keywords")
        keywords = []
        today = datetime.now().date()
        with self.db_client.session_factory() as session:
            cases = session.query(
                lds.Case,
                sa.func.array_agg(lds.Keyword.id),
                sa.func.min(lds.Keyword.updated_at)
            ).join(lds.Keyword, lds.Keyword.case_id == lds.Case.id)
            cases = cases.where(
                sa.and_(
                    lds.Case.inactive == False,  # noqa
                    sa.or_(lds.Case.end_date == None, lds.Case.end_date >= today),  # noqa
                )
            )
            cases = cases.group_by(lds.Case.id).all()
            now = datetime.now(timezone.utc)
            for case in cases:
                if case[2] > (now - get_threshold(case[0].repeat)):
                    logging.warning("Skipping case %s because of repeat %s", case[0].id, case[0].repeat)
                else:
                    keywords.extend(case[1])
        logging.warning("Today's keywords are: %s", keywords)
        return keywords

    # -------------------------------------
    # Users
    # -------------------------------------
    def create_user(self, user_id, name, email):
        with self.db_client.session_factory() as session:
            values = {
                "id": user_id,
                "name": name,
                "mail": email,
                "role": lds.User.Roles.USER,
            }
            stmt = insert(lds.User).values(values)
            do_update_stmt = stmt.on_conflict_do_update(
                constraint="users_pkey",
                set_={x: getattr(stmt.excluded, x) for x in ["name", "mail"]},
            )
            session.execute(do_update_stmt)
            session.commit()
