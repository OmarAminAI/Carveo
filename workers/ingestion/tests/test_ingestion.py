import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from worker.ingestion import (
    ExtractedListing,
    IngestionService,
    RefreshQuery,
    RefreshScheduler,
    SourceConfig,
    SourceNotApprovedError,
)


class FakeAdapter:
    source_id = "fixture"

    async def discover(self, query: RefreshQuery) -> list[str]:
        return ["https://example.test/listing/1"]

    async def extract(self, url: str) -> ExtractedListing:
        return ExtractedListing(source_listing_id="1", source_url=url, fields={"title": "Fixture car"}, confidence=.9)


def test_unapproved_source_cannot_crawl() -> None:
    service = IngestionService({"fixture": SourceConfig(source_id="fixture", market="AE")}, {"fixture": FakeAdapter()})
    with pytest.raises(SourceNotApprovedError):
        asyncio.run(service.refresh("fixture", RefreshQuery(market="AE", make="Toyota", model="Land Cruiser")))


def test_scheduler_deduplicates_hourly_refreshes() -> None:
    scheduler = RefreshScheduler()
    query = RefreshQuery(market="AE", make="Toyota", model="Land Cruiser", year=2022)
    now = datetime.now(timezone.utc)
    assert scheduler.should_enqueue(query, now)
    assert not scheduler.should_enqueue(query, now + timedelta(minutes=20))
    assert scheduler.should_enqueue(query, now + timedelta(hours=1))


def test_approved_adapter_extracts_listings() -> None:
    service = IngestionService({"fixture": SourceConfig(source_id="fixture", market="AE", enabled=True, authorization_status="approved")}, {"fixture": FakeAdapter()})
    result = asyncio.run(service.refresh("fixture", RefreshQuery(market="AE", make="Toyota", model="Land Cruiser")))
    assert result[0].fields["title"] == "Fixture car"
