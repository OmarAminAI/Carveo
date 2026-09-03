from __future__ import annotations

from datetime import UTC, datetime

import pytest
from carveo_core.ingestion_contracts import (
    ListingReference,
    NormalizedListing,
    RawConditionClaim,
    RawListing,
    RawPhoto,
    RejectedListing,
)
from carveo_worker.normalization import normalize_listing

NOW = datetime(2026, 9, 3, 12, 0, tzinfo=UTC)


def raw_listing(**changes: object) -> RawListing:
    values: dict[str, object] = {
        "reference": ListingReference(
            source_key="carveo-fixture",
            source_listing_id="fixture-001",
            canonical_url="http://fixture-origin:8080/listings/fixture-001.html",
            discovered_at=NOW,
            search_page_key="popular-uae:baseline:1",
        ),
        "title": "Toyota RAV4 Adventure",
        "make": "Toyota",
        "model": "RAV4",
        "trim": "Adventure",
        "year": "2023 model",
        "price": "AED 118,500",
        "currency": "aed",
        "mileage": "31,000 km",
        "city": "Dubai, UAE",
        "body_type": "sport utility vehicle",
        "specifications": "GCC Specs",
        "seller_type": "dealership",
        "description": "Source description",
        "features": ["Sunroof", "Adaptive cruise"],
        "photos": [
            RawPhoto(source_url="http://fixture-origin:8080/media/front.jpg", source_media_id="front"),
            RawPhoto(source_url="http://fixture-origin:8080/media/rear.jpg", source_media_id="rear"),
        ],
        "condition_claims": [
            RawConditionClaim(
                kind="warning",
                label="Damage stated",
                detail="Seller states one repaired panel.",
                source_claim="Repaired rear panel",
                confidence=0.95,
            )
        ],
        "source_sold": False,
        "extraction_path": "json-ld",
        "extracted_at": NOW,
    }
    values.update(changes)
    return RawListing.model_validate(values)


def test_normalizes_uae_market_values_and_preserves_original_audit_text() -> None:
    result = normalize_listing(raw_listing(), NOW)

    assert isinstance(result, NormalizedListing)
    assert result.price == 118_500
    assert result.currency == "AED"
    assert result.mileage_km == 31_000
    assert result.year == 2023
    assert result.city == "Dubai"
    assert result.body_type == "SUV"
    assert result.specifications == "GCC"
    assert result.seller_type == "Dealer"
    assert result.original_values == {
        "body_type": "sport utility vehicle",
        "city": "Dubai, UAE",
        "currency": "aed",
        "description": "Source description",
        "make": "Toyota",
        "mileage": "31,000 km",
        "model": "RAV4",
        "price": "AED 118,500",
        "seller_type": "dealership",
        "specifications": "GCC Specs",
        "title": "Toyota RAV4 Adventure",
        "trim": "Adventure",
        "year": "2023 model",
    }


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("GCC", "GCC"),
        ("US specs", "American"),
        ("European import", "European"),
        ("Japan specifications", "Japanese"),
    ],
)
def test_normalizes_regional_specification_aliases(raw_value: str, expected: str) -> None:
    result = normalize_listing(raw_listing(specifications=raw_value), NOW)

    assert isinstance(result, NormalizedListing)
    assert result.specifications == expected


@pytest.mark.parametrize(
    ("city", "seller_type", "expected_city", "expected_seller"),
    [
        ("AUH", "owner", "Abu Dhabi", "Private"),
        ("Sharjah, United Arab Emirates", "private seller", "Sharjah", "Private"),
        ("AJMAN", "showroom", "Ajman", "Dealer"),
    ],
)
def test_normalizes_city_and_seller_aliases(
    city: str,
    seller_type: str,
    expected_city: str,
    expected_seller: str,
) -> None:
    result = normalize_listing(raw_listing(city=city, seller_type=seller_type), NOW)

    assert isinstance(result, NormalizedListing)
    assert result.city == expected_city
    assert result.seller_type == expected_seller


def test_photo_order_and_source_media_identity_are_preserved() -> None:
    result = normalize_listing(raw_listing(), NOW)

    assert isinstance(result, NormalizedListing)
    assert [photo.source_media_id for photo in result.photos] == ["front", "rear"]
    assert [photo.provenance for photo in result.photos] == ["fixture", "fixture"]


def test_absent_condition_claims_become_unknown_not_positive() -> None:
    result = normalize_listing(raw_listing(condition_claims=[]), NOW)

    assert isinstance(result, NormalizedListing)
    assert [(item.kind, item.label) for item in result.condition_evidence] == [
        ("unknown", "Condition not stated")
    ]


def test_source_condition_claim_is_preserved_without_strengthening_it() -> None:
    result = normalize_listing(raw_listing(), NOW)

    assert isinstance(result, NormalizedListing)
    assert result.condition_evidence[0].kind == "warning"
    assert result.condition_evidence[0].source_claim == "Repaired rear panel"
    assert result.condition_evidence[0].confidence == 0.95


def test_arabic_title_and_description_remain_unchanged() -> None:
    result = normalize_listing(
        raw_listing(
            title="تويوتا كامري جي إل إي",
            description="سيارة تجريبية مكتوبة بالعربية لاختبار الحفاظ على النص الأصلي.",
        ),
        NOW,
    )

    assert isinstance(result, NormalizedListing)
    assert result.title == "تويوتا كامري جي إل إي"
    assert result.description == "سيارة تجريبية مكتوبة بالعربية لاختبار الحفاظ على النص الأصلي."
    assert result.original_values["title"] == "تويوتا كامري جي إل إي"


@pytest.mark.parametrize(
    ("changes", "error_code"),
    [
        ({"mileage": "100 SMOOT"}, "unsupported_mileage_unit"),
        ({"price": None}, "missing_price"),
        ({"currency": "USD"}, "unsupported_currency"),
        ({"year": "1899"}, "invalid_year"),
        ({"city": "Al Ain"}, "unsupported_city"),
        ({"body_type": "Motorcycle"}, "unsupported_body_type"),
        ({"specifications": "Unknown"}, "unsupported_specifications"),
        ({"seller_type": "Auction"}, "unsupported_seller_type"),
        ({"trim": None}, "missing_trim"),
    ],
)
def test_invalid_or_unsupported_required_values_are_bounded_rejections(
    changes: dict[str, object],
    error_code: str,
) -> None:
    result = normalize_listing(raw_listing(**changes), NOW)

    assert isinstance(result, RejectedListing)
    assert result.error_code == error_code
    assert len(result.detail) <= 400


def test_invalid_reference_url_is_rejected_before_normalization() -> None:
    invalid_reference = raw_listing().reference.model_copy(update={"canonical_url": "file:///private/listing.html"})

    result = normalize_listing(raw_listing(reference=invalid_reference), NOW)

    assert isinstance(result, RejectedListing)
    assert result.error_code == "invalid_source_url"


def test_invalid_photo_url_rejects_the_record_without_reordering_remaining_media() -> None:
    result = normalize_listing(raw_listing(photos=[RawPhoto(source_url="file:///private/front.jpg")]), NOW)

    assert isinstance(result, RejectedListing)
    assert result.error_code == "invalid_photo_url"


def test_kmt_fixture_unit_is_normalized_to_kilometres() -> None:
    result = normalize_listing(raw_listing(mileage="33000 KMT"), NOW)

    assert isinstance(result, NormalizedListing)
    assert result.mileage_km == 33_000
