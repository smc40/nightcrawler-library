import enum

from sqlalchemy import Column, Integer, String, ForeignKey, Enum, func, \
    Boolean
from sqlalchemy.orm import declarative_base

from libnightcrawler.db.utc_date_time import UtcDateTime

Base = declarative_base()

class Tenant(Base):
    __tablename__ = 'tenants'

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String, nullable=False, index=True)
    countries = Column(String, nullable=False)
    languages = Column(String, nullable=False)


class FilterList(Base):
    __tablename__ = 'filter_list'
    class FilterListType(str, enum.Enum):
        WHITELIST = "whitelist"
        BLACKLIST = "blacklist"
    class FilterListStatus(str, enum.Enum):
        ACTIVE = "active"
        DELETED = "deleted"

    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
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
    __tablename__ = 'cases'

    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    notifications_enabled = Column(Boolean, nullable=False, default=False)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())
    inactive = Column(Boolean, nullable=False, default=False)
    inactive_at = Column(UtcDateTime, nullable=True)


class CaseMember(Base):
    __tablename__ = 'case_members'

    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    case_id = Column(Integer, ForeignKey('cases.id', ondelete='CASCADE'), index=True)
    user_id = Column(String, primary_key=True)


class Cost(Base):
    __tablename__ = 'costs'

    class Unit(str, enum.Enum):
        UNIT = "unit"
        ZYTE = "zyte"

    tenant_id = Column(Integer, ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    id = Column(Integer, primary_key=True, nullable=False)
    case_id: int = Column(Integer, ForeignKey('cases.id', ondelete='CASCADE'), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    unit = Column(String, nullable=False)
    created_at = Column(UtcDateTime, nullable=False, server_default=func.now())


COST_UNIT_FACTOR = {
    Cost.Unit.UNIT.value : 1,
    Cost.Unit.ZYTE.value : 3,
}
