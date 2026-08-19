"""Compliant ingestion primitives; adapters stay disabled until a source is approved."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Protocol


@dataclass(frozen=True)
class SourceConfig:
    source_id: str
    market: str
    enabled: bool = False
    authorization_status: str = "pending_approval"
    rate_limit_per_minute: int = 0
    adapter_version: str = "v1"


@dataclass(frozen=True)
class RefreshQuery:
    market: str
    make: str
    model: str
    year: int | None = None
    profile_id: str | None = None

    @property
    def key(self) -> str:
        return ":".join([self.market, self.make.casefold(), self.model.casefold(), str(self.year or "any"), self.profile_id or "popular"])


@dataclass
class ExtractedListing:
    source_listing_id: str
    source_url: str
    fields: dict[str, object]
    evidence: dict[str, str] = field(default_factory=dict)
    confidence: float = 0.0


class SourceAdapter(Protocol):
    source_id: str

    async def discover(self, query: RefreshQuery) -> list[str]: ...
    async def extract(self, url: str) -> ExtractedListing: ...


class SourceNotApprovedError(RuntimeError):
    pass


class RefreshScheduler:
    def __init__(self, minimum_interval: timedelta = timedelta(hours=1)) -> None:
        self.minimum_interval = minimum_interval
        self._last_enqueued: dict[str, datetime] = {}

    def should_enqueue(self, query: RefreshQuery, now: datetime | None = None) -> bool:
        now = now or datetime.now(timezone.utc)
        previous = self._last_enqueued.get(query.key)
        if previous and now - previous < self.minimum_interval:
            return False
        self._last_enqueued[query.key] = now
        return True


class IngestionService:
    def __init__(self, sources: dict[str, SourceConfig], adapters: dict[str, SourceAdapter], scheduler: RefreshScheduler | None = None) -> None:
        self.sources = sources
        self.adapters = adapters
        self.scheduler = scheduler or RefreshScheduler()

    async def refresh(self, source_id: str, query: RefreshQuery) -> list[ExtractedListing]:
        source = self.sources[source_id]
        if not source.enabled or source.authorization_status != "approved":
            raise SourceNotApprovedError(f"{source_id} is not approved for ingestion")
        if not self.scheduler.should_enqueue(query):
            return []
        adapter = self.adapters[source_id]
        urls = await adapter.discover(query)
        return [await adapter.extract(url) for url in urls]


DUBIZZLE_UAE = SourceConfig(source_id="dubizzle", market="AE")
