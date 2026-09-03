from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from carveo_core.ingestion_contracts import (
    CrawlRunItemResult,
    CrawlRunSummary,
    ListingReference,
    MediaCacheResult,
    NormalizedListing,
    NormalizedPhoto,
    RawListing,
    RejectedListing,
    SourceProfile,
    SourceQuery,
)
from pydantic import ValidationError

NOW = datetime(2026, 9, 3, 12, tzinfo=UTC)


def _reference() -> ListingReference:
    return ListingReference(
        source_key="carveo-fixture",
        source_listing_id="fixture-001",
        canonical_url="http://fixture-origin:8080/listings/fixture-001.html",
        discovered_at=NOW,
        search_page_key="popular-uae:1",
    )


def _normalized_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "reference": _reference(),
        "market": "ae",
        "title": "Toyota RAV4",
        "make": "Toyota",
        "model": "RAV4",
        "trim": "Adventure",
        "year": 2023,
        "price": 118_000,
        "currency": "AED",
        "mileage_km": 31_000,
        "city": "Dubai",
        "body_type": "SUV",
        "specifications": "GCC",
        "seller_type": "Dealer",
        "description": "Synthetic fixture listing.",
        "features": ["Adaptive cruise control"],
        "photos": [
            NormalizedPhoto(
                source_url="http://fixture-origin:8080/media/rav4-1.webp",
                provenance="fixture",
                source_media_id="rav4-1",
            )
        ],
        "condition_evidence": [],
        "source_sold": False,
        "original_values": {"title": "Toyota RAV4", "price": "AED 118,000"},
        "extracted_at": NOW,
    }
    payload.update(overrides)
    return payload


def test_normalized_listing_preserves_arabic_source_text() -> None:
    listing = NormalizedListing.model_validate(
        _normalized_payload(title="تويوتا راف فور", original_values={"title": "تويوتا راف فور"})
    )

    assert listing.title == "تويوتا راف فور"
    assert listing.make == "Toyota"
    assert listing.original_values["title"] == "تويوتا راف فور"


def test_queue_facing_source_query_contains_no_url() -> None:
    assert "url" not in SourceQuery.model_fields
    assert SourceQuery(query_key="popular-uae", fixture_scenario="baseline").market == "ae"


def test_contracts_reject_extra_fields_and_non_utc_timestamps() -> None:
    with pytest.raises(ValidationError):
        SourceQuery(query_key="popular-uae", fixture_scenario="baseline", url="https://example.com")

    with pytest.raises(ValidationError):
        ListingReference(
            source_key="carveo-fixture",
            source_listing_id="fixture-001",
            canonical_url="http://fixture-origin:8080/listings/fixture-001.html",
            discovered_at=datetime(2026, 9, 3, 12, tzinfo=timezone(timedelta(hours=2))),
            search_page_key="popular-uae:1",
        )


def test_source_profile_bounds_operational_limits() -> None:
    profile = SourceProfile(
        id=uuid4(),
        key="carveo-fixture",
        market="ae",
        authorization_status="fixture",
        enabled=True,
        environment_allowlist=["development", "test"],
        allowed_hosts=["fixture-origin"],
        allowed_schemes=["http"],
        terms_reviewed_at=NOW,
        adapter_version="fixture-v1",
        parser_version="fixture-parser-v1",
        concurrency_limit=2,
        rate_limit_per_minute=30,
    )

    assert profile.concurrency_limit == 2
    with pytest.raises(ValidationError):
        profile.model_copy(update={"concurrency_limit": 0}, deep=True).__class__.model_validate(
            {**profile.model_dump(), "concurrency_limit": 0}
        )


def test_ingestion_result_contracts_are_strict_and_json_safe() -> None:
    run_id = uuid4()
    item_id = uuid4()
    summary = CrawlRunSummary(
        id=run_id,
        source_key="carveo-fixture",
        trigger="manual",
        status="completed",
        discovery_complete=True,
        counters={"created": 1},
        queued_at=NOW,
        started_at=NOW,
        finished_at=NOW,
    )
    item = CrawlRunItemResult(
        run_item_id=item_id,
        outcome="created",
        listing_public_id="fixture-001",
    )
    rejected = RejectedListing(reference=_reference(), error_code="missing_price", detail="Required price missing")
    media = MediaCacheResult(
        listing_id=uuid4(),
        outcome="updated",
        photo_ids=[uuid4()],
        obsolete_storage_keys=["sha256/ab/old.webp"],
    )

    assert summary.model_dump(mode="json")["id"] == str(run_id)
    assert item.outcome == "created"
    assert rejected.error_code == "missing_price"
    assert media.outcome == "updated"


def test_raw_listing_accepts_missing_source_fields_for_later_rejection() -> None:
    raw = RawListing(
        reference=_reference(),
        title="Toyota RAV4",
        make="Toyota",
        model="RAV4",
        trim=None,
        year="2023",
        price=None,
        currency="AED",
        mileage="31,000 km",
        city="Dubai",
        body_type="SUV",
        specifications="GCC",
        seller_type="Dealer",
        description="Synthetic fixture listing.",
        features=[],
        photos=[],
        condition_claims=[],
        source_sold=False,
        extraction_path="json-ld",
        extracted_at=NOW,
    )

    assert raw.price is None
    with pytest.raises(ValidationError):
        NormalizedListing.model_validate(_normalized_payload(price=-1))
