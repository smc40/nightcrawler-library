from datetime import datetime
from enum import Enum, auto
from dataclasses import dataclass


class EntryType(str, Enum):
    KEYWORD = auto()
    IMAGE = auto()


class CaseStatus(str, Enum):
    PENDING = auto()
    SUCCEEDED = auto()
    FAILED = auto()
    TIMEOUT = auto()


@dataclass
class Tenant:
    id: str
    country_codes: list[str]
    languages: list[str]
    blacklist: list[str]


@dataclass
class CaseMetaData:
    tenant_id: str
    id: str
    name: str
    crawl_status: CaseStatus
    members: list[str]


@dataclass
class Offer:
    url: str
    root: str
    title: str
    text: str
    price: str
    score: float
    created: datetime
    last_updated: datetime
