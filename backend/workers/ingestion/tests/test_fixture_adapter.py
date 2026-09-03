from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from carveo_core.ingestion_contracts import ListingReference, RawListing, RejectedListing, SourceProfile, SourceQuery
from carveo_worker.adapters.fixture import FixtureSourceAdapter
from carveo_worker.crawl4ai_client import CrawlDocument
from carveo_worker.source_policy import SourcePolicy, SourcePolicyError

NOW = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)
SITE_ROOT = Path(__file__).parents[3] / "infra" / "fixtures" / "site"


class FixtureFileClient:
    def __init__(self, *, overrides: dict[str, CrawlDocument] | None = None) -> None:
        self.requested_urls: list[str] = []
        self._overrides = overrides or {}

    async def crawl(self, urls: Sequence[str]) -> list[CrawlDocument]:
        documents: list[CrawlDocument] = []
        for url in urls:
            self.requested_urls.append(url)
            if url in self._overrides:
                documents.append(self._overrides[url])
                continue
            relative_path = url.removeprefix("http://fixture-origin:8080/")
            documents.append(
                CrawlDocument(
                    url=url,
                    html=(SITE_ROOT / relative_path).read_text(encoding="utf-8"),
                    status_code=200,
                    success=True,
                )
            )
        return documents


def source_profile(**changes: object) -> SourceProfile:
    values: dict[str, object] = {
        "id": UUID("00000000-0000-0000-0000-000000000001"),
        "key": "carveo-fixture",
        "market": "ae",
        "authorization_status": "fixture",
        "enabled": True,
        "environment_allowlist": ["development", "test"],
        "allowed_hosts": ["fixture-origin"],
        "allowed_schemes": ["http"],
        "terms_reviewed_at": NOW,
        "adapter_version": "fixture-v1",
        "parser_version": "fixture-parser-v1",
        "concurrency_limit": 2,
        "rate_limit_per_minute": 30,
    }
    values.update(changes)
    return SourceProfile.model_validate(values)


def adapter(client: FixtureFileClient, **profile_changes: object) -> FixtureSourceAdapter:
    return FixtureSourceAdapter.from_manifest_path(
        profile=source_profile(**profile_changes),
        policy=SourcePolicy(),
        client=client,
        environment="test",
        manifest_path=SITE_ROOT / "scenarios.json",
        clock=lambda: NOW,
    )


@pytest.mark.anyio
async def test_discovery_builds_manifest_urls_and_collapses_duplicate_source_identity() -> None:
    client = FixtureFileClient()
    result = await adapter(client).discover(
        SourceQuery(query_key="popular-uae", fixture_scenario="baseline")
    )

    assert len(result.references) == 12
    assert [reference.source_listing_id for reference in result.references].count("fixture-006") == 1
    assert result.references[0].canonical_url == "http://fixture-origin:8080/listings/fixture-001.html"
    assert result.visited_pages == [
        "http://fixture-origin:8080/search/baseline-page-1.html",
        "http://fixture-origin:8080/search/baseline-page-2.html",
    ]
    assert result.discovery_complete is True
    assert result.error_code is None


@pytest.mark.anyio
async def test_policy_blocks_adapter_before_any_client_call() -> None:
    client = FixtureFileClient()

    with pytest.raises(SourcePolicyError, match="source_disabled"):
        await adapter(client, enabled=False).discover(
            SourceQuery(query_key="popular-uae", fixture_scenario="baseline")
        )

    assert client.requested_urls == []


@pytest.mark.anyio
async def test_valid_json_ld_wins_over_conflicting_css_values() -> None:
    client = FixtureFileClient()
    reference = ListingReference(
        source_key="carveo-fixture",
        source_listing_id="fixture-001",
        canonical_url="http://fixture-origin:8080/listings/fixture-001.html",
        discovered_at=NOW,
        search_page_key="popular-uae:baseline:1",
    )
    original = (SITE_ROOT / "listings" / "fixture-001.html").read_text(encoding="utf-8")
    mixed = original.replace("<h1>Toyota RAV4 Adventure</h1>", "<h1 data-carveo-title>Wrong CSS title</h1>")
    client._overrides[reference.canonical_url] = CrawlDocument(
        url=reference.canonical_url,
        html=mixed,
        status_code=200,
        success=True,
    )

    result = await adapter(client).extract(reference)

    assert isinstance(result, RawListing)
    assert result.extraction_path == "json-ld"
    assert result.title == "Toyota RAV4 Adventure"
    assert result.photos[0].source_url == "http://fixture-origin:8080/media/fixture-suv.jpg"


@pytest.mark.anyio
async def test_css_fallback_extracts_listing_when_json_ld_is_absent() -> None:
    client = FixtureFileClient()
    reference = ListingReference(
        source_key="carveo-fixture",
        source_listing_id="fixture-011",
        canonical_url="http://fixture-origin:8080/listings/fixture-011.html",
        discovered_at=NOW,
        search_page_key="popular-uae:baseline:2",
    )

    result = await adapter(client).extract(reference)

    assert isinstance(result, RawListing)
    assert result.extraction_path == "css"
    assert result.title == "Honda Civic Sport"
    assert result.price == "AED 92000"


@pytest.mark.anyio
async def test_arabic_source_text_is_preserved_verbatim() -> None:
    client = FixtureFileClient()
    reference = ListingReference(
        source_key="carveo-fixture",
        source_listing_id="fixture-012",
        canonical_url="http://fixture-origin:8080/listings/fixture-012.html",
        discovered_at=NOW,
        search_page_key="popular-uae:baseline:2",
    )

    result = await adapter(client).extract(reference)

    assert isinstance(result, RawListing)
    assert result.title == "تويوتا كامري جي إل إي"
    assert result.description == "سيارة تجريبية مكتوبة بالعربية لاختبار الحفاظ على النص الأصلي."


@pytest.mark.anyio
async def test_malformed_json_ld_is_rejected_instead_of_silently_using_css() -> None:
    client = FixtureFileClient()
    reference = ListingReference(
        source_key="carveo-fixture",
        source_listing_id="failure-malformed",
        canonical_url="http://fixture-origin:8080/listings/failure-malformed.html",
        discovered_at=NOW,
        search_page_key="popular-uae:failures:1",
    )

    result = await adapter(client).extract(reference)

    assert isinstance(result, RejectedListing)
    assert result.error_code == "malformed_json_ld"
    assert "invalid}" not in result.detail


@pytest.mark.anyio
async def test_failed_or_incomplete_search_page_never_reports_complete_discovery() -> None:
    first_url = "http://fixture-origin:8080/search/baseline-page-1.html"
    client = FixtureFileClient(
        overrides={
            first_url: CrawlDocument(
                url=first_url,
                html="",
                status_code=200,
                success=False,
                error="blocked",
            )
        }
    )

    result = await adapter(client).discover(
        SourceQuery(query_key="popular-uae", fixture_scenario="baseline")
    )

    assert result.discovery_complete is False
    assert result.error_code == "blocked"
    assert len(result.references) == 7
