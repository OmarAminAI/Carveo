from datetime import UTC, datetime

import pytest
from carveo_core.ingestion_contracts import ListingReference
from carveo_worker.identity import (
    SourceIdentityError,
    canonicalize_source_url,
    resolve_source_identity,
)

NOW = datetime(2026, 9, 3, tzinfo=UTC)


def reference(source_listing_id: str | None) -> ListingReference:
    return ListingReference(
        source_key="carveo-fixture",
        source_listing_id=source_listing_id,
        canonical_url="HTTP://FIXTURE-ORIGIN:80/listings/fixture-001/?utm_source=test&trim=Adventure#photos",
        discovered_at=NOW,
        search_page_key="popular-uae:1",
    )


def test_canonicalize_source_url_normalizes_host_path_query_and_tracking() -> None:
    actual = canonicalize_source_url(
        "HTTP://FIXTURE-ORIGIN:80/listings/fixture-001/?utm_source=test&z=2&trim=Adventure&a=1#photos"
    )

    assert actual == "http://fixture-origin/listings/fixture-001?a=1&trim=Adventure&z=2"


def test_canonicalize_source_url_retains_non_default_port_and_repeated_semantic_values() -> None:
    actual = canonicalize_source_url("http://fixture-origin:8080/search?make=Toyota&make=Lexus")

    assert actual == "http://fixture-origin:8080/search?make=Lexus&make=Toyota"


def test_source_listing_id_is_primary_identity() -> None:
    identity = resolve_source_identity(reference("fixture-001"), canonical_url_matches=[])

    assert identity.key == "carveo-fixture:fixture-001"
    assert identity.source_listing_id == "fixture-001"


def test_exact_single_url_match_is_guarded_fallback() -> None:
    identity = resolve_source_identity(reference(None), canonical_url_matches=["existing-source-id"])

    assert identity.source_listing_id == "existing-source-id"
    assert identity.canonical_url == "http://fixture-origin/listings/fixture-001?trim=Adventure"


@pytest.mark.parametrize(
    ("matches", "error_code"),
    [([], "source_identity_missing"), (["one", "two"], "source_identity_ambiguous")],
)
def test_url_fallback_rejects_zero_or_ambiguous_matches(matches: list[str], error_code: str) -> None:
    with pytest.raises(SourceIdentityError) as raised:
        resolve_source_identity(reference(None), canonical_url_matches=matches)

    assert raised.value.code == error_code


@pytest.mark.parametrize("url", ["", "relative/path", "ftp://fixture-origin/item", "http:///item"])
def test_canonicalization_rejects_invalid_absolute_http_urls(url: str) -> None:
    with pytest.raises(SourceIdentityError) as raised:
        canonicalize_source_url(url)

    assert raised.value.code == "invalid_source_url"
