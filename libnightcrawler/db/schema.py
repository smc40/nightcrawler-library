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
)
from sqlalchemy.orm import declarative_base

from libnightcrawler.db.utc_date_time import UtcDateTime

Base = declarative_base()


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())
    user_id = Column(String, nullable=False, index=True)
    operation = Column(String, nullable=False, index=True)
    payload = Column(JSON, nullable=False)


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False, index=True)
    countries = Column(String, nullable=False)
    languages = Column(String, nullable=False)
    currencies = Column(String, nullable=False)
    unit = Column(String, nullable=False)


class User(Base):
    __tablename__ = "users"

    class Roles(str, enum.Enum):
        ADMIN = enum.auto()
        USER = enum.auto()

    id = Column(String, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    mail = Column(String, nullable=False)
    org_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(Enum(Roles), nullable=False)


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
    type = Column(Enum(FilterListType), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    status = Column(Enum(FilterListStatus), nullable=False)
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


class CaseMember(Base):
    __tablename__ = "case_members"

    case_id = Column(Integer, index=True, nullable=False, primary_key=True)
    user_id = Column(String, index=True, nullable=False, primary_key=True)


class Cost(Base):
    __tablename__ = "costs"

    class Unit(str, enum.Enum):
        UNIT = "unit"
        ZYTE = "zyte"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    case_id: int = Column(Integer, primary_key=True, nullable=False, index=True)
    value = Column(Integer, nullable=False)
    unit = Column(String, nullable=False)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())


COST_UNIT_FACTOR = {
    Cost.Unit.UNIT.value: 1,
    Cost.Unit.ZYTE.value: 3,
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
    case_id: int = Column(Integer, nullable=False, primary_key=True, index=True)
    notifications_enabled = Column(Boolean, nullable=False, default=False)
    query = Column(String, nullable=False)
    type = Column(Enum(KeywordType), nullable=False)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())
    description = Column(String, nullable=True)
    crawl_state = Column(Enum(CrawlState), nullable=False)

    Index("uq_keywords_query_type_case_id", query, type, case_id, unique=True)


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    case_id: int = Column(Integer, nullable=False, primary_key=True, index=True)
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
    uid = Column(String, nullable=False)
    root = Column(String, nullable=False)
    relevant = Column(Boolean, nullable=False, default=True)
    images = Column(JSON, nullable=True)


class OverallBookmark(Base):
    __tablename__ = "overall_bookmark"

    user_id = Column(String, primary_key=True)
    offer_id = Column(Integer, nullable=False, primary_key=True)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())
