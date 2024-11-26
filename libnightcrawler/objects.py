from dataclasses import dataclass
from libnightcrawler.db.schema import Offer


@dataclass
class Organization:
    name: str
    unit: str
    blacklist: list[str]
    whitelist: list[str]


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
    number_of_results: int = 50
    page_type_detection_method: str = "zyte"
    enrich_keyword: bool = False

    def new_result(self, **kwargs):
        images = kwargs.pop("images", None)
        return CrawlResult(
            request=self,
            offer=Offer(case_id=self.case_id, keyword_id=self.keyword_id, **kwargs),
            images=(images or []),
        )


@dataclass
class CrawlResult:
    request: CrawlRequest
    offer: Offer
    images: list[str]
