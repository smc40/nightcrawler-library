import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Enum,
    func,
    Boolean,
    Index,
    JSON,
    Numeric,
    UniqueConstraint,
    Date,
    Table,
)
from sqlalchemy.orm import DeclarativeBase, mapped_column

from libnightcrawler.db.utc_date_time import UtcDateTime


class Base(DeclarativeBase):
    pass


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())
    case_id = Column(Integer, nullable=False, index=True, default=0)
    operation = Column(String, nullable=False, index=True)
    payload = Column(JSON, nullable=False)


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False, index=True)
    unit = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"

    class Roles(str, enum.Enum):
        ADMIN = enum.auto()
        USER = enum.auto()
        SUPERADMIN = enum.auto()

    id = Column(String, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    mail = Column(String, nullable=False)
    role = mapped_column(Enum(Roles), nullable=False, default=Roles.USER, server_default='USER')


# Many-to-many relation table
UserOrganizations = Table(
    "user_organizations",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("org_id", ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
)


class FilterList(Base):
    __tablename__ = "filter_list"

    class FilterListType(str, enum.Enum):
        WHITELIST = "whitelist"
        BLACKLIST = "blacklist"

    class FilterListStatus(str, enum.Enum):
        ACTIVE = "active"
        DELETED = "deleted"

    org_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    id = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    type = mapped_column(Enum(FilterListType), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    status = mapped_column(Enum(FilterListStatus), nullable=False)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())
    updated_at = Column(UtcDateTime, nullable=False, server_default=func.now())
    deleted_at = Column(UtcDateTime, nullable=True)
    created_by = Column(String, nullable=False)
    deleted_by = Column(String, nullable=True)


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    org_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False)
    notifications_enabled = Column(Boolean, nullable=False, default=False)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())
    inactive = Column(Boolean, nullable=False, default=False)
    inactive_at = Column(UtcDateTime, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    repeat = Column(String, nullable=False, default="daily", server_default="daily")


class CaseMember(Base):
    __tablename__ = "case_members"

    case_id = Column(Integer, index=True, nullable=False, primary_key=True)
    user_id = Column(String, index=True, nullable=False, primary_key=True)


class Usage(Base):
    __tablename__ = "usages"

    class Unit(str, enum.Enum):
        UNIT = "unit"
        ZYTE = "zyte"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    case_id = Column(Integer, primary_key=True, nullable=False, index=True)
    value = Column(Integer, nullable=False)
    unit = Column(String, nullable=False)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())


USAGE_UNIT_FACTOR = {
    Usage.Unit.UNIT.value: 1,
    Usage.Unit.ZYTE.value: 3,
}


class Keyword(Base):
    __tablename__ = "keywords"

    class KeywordType(str, enum.Enum):
        TEXT = "text"
        IMAGE = "image"
        URL = "url"

    class CrawlState(enum.Enum):
        PENDING = enum.auto()
        SUCCEEDED = enum.auto()
        FAILED = enum.auto()
        TIMEOUT = enum.auto()

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    case_id = Column(Integer, nullable=False, primary_key=True, index=True)
    notifications_enabled = Column(Boolean, nullable=False, default=False)
    query = Column(String, nullable=False)
    type = mapped_column(Enum(KeywordType), nullable=False)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())
    updated_at = Column(UtcDateTime, nullable=False, server_default=func.now())
    description = Column(String, nullable=True)
    crawl_state = mapped_column(Enum(CrawlState), nullable=False)
    error = Column(String, nullable=True)

    Index("uq_keywords_query_type_case_id", query, type, case_id, unique=True)


class Offer(Base):
    __tablename__ = "offers"

    class OfferStatus(str, enum.Enum):
        UNPROCESSED = enum.auto()
        BOOKMARKED = enum.auto()
        IN_PROGRESS = enum.auto()
        CONFIRMED = enum.auto()
        DISMISSED = enum.auto()
        NOT_RELEVANT = enum.auto()
        NEVER_RELEVANT = enum.auto()
        FILTERED = enum.auto()
        ERROR = enum.auto()

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    case_id = Column(Integer, nullable=False, primary_key=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String, nullable=False)
    text = Column(String, nullable=False)
    price = Column(String, nullable=True)
    keyword_id = Column(Integer, nullable=False, index=True)
    platform = Column(String, nullable=False)
    source = Column(String, nullable=False)
    language = Column(String, nullable=False)
    score = Column(Numeric, nullable=False)
    crawled_at = Column(UtcDateTime, nullable=False, server_default=func.now())
    uid = mapped_column(String, nullable=False)
    root = Column(String, nullable=False)
    relevant = Column(Boolean, nullable=False, default=True)
    images = Column(JSON, nullable=True)
    status = mapped_column(Enum(OfferStatus), nullable=False, default=OfferStatus.UNPROCESSED, server_default='UNPROCESSED')
    __table_args__ = (UniqueConstraint("uid", "case_id", name="uq_offers_uid_case_id"),)

    def to_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


class OverallBookmark(Base):
    __tablename__ = "overall_bookmark"

    user_id = Column(String, primary_key=True)
    offer_id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())
