from dataclasses import dataclass
from libnightcrawler.db.schema import Offer


@dataclass
class Organization:
    name: str
    unit: str
    countries: list[str]
    languages: list[str]
    currencies: list[str]
    blacklist: list[str]


@dataclass
class Image:
    url: str
    path: str
    description: str
    blob: str | None = None


@dataclass
class CrawlRequest:
    keyword_type: str
    keyword_value: str
    organization: Organization
    keyword_id: int = 0
    case_id: int = 0

    def new_result(self, **kwargs):
        return CrawlResult(
            request=self, offer=Offer(case_id=self.case_id, keyword_id=self.keyword_id, **kwargs)
        )


@dataclass
class CrawlResult:
    request: CrawlRequest
    offer: Offer
