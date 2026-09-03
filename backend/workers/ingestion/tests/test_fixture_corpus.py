import json
import re
from pathlib import Path
from urllib.parse import urlsplit

FIXTURE_ROOT = Path(__file__).parents[3] / "infra" / "fixtures" / "site"
THIRD_PARTY_MEDIA_ROOT = Path(__file__).parents[4] / "frontend" / "public" / "media"


def load_manifest() -> dict[str, object]:
    return json.loads((FIXTURE_ROOT / "scenarios.json").read_text(encoding="utf-8"))


def test_manifest_defines_immutable_lifecycle_scenarios() -> None:
    manifest = load_manifest()

    assert manifest["version"] == 1
    assert set(manifest["scenarios"]) == {
        "baseline",
        "unchanged",
        "changed",
        "missing-1",
        "missing-2",
        "removed",
        "restored",
        "failures",
    }


def test_every_manifest_page_exists_and_uses_private_fixture_origin() -> None:
    manifest = load_manifest()
    scenarios = manifest["scenarios"]
    assert isinstance(scenarios, dict)

    for scenario in scenarios.values():
        assert isinstance(scenario, dict)
        pages = scenario["searchPages"]
        assert isinstance(pages, list)
        for page_url in pages:
            assert isinstance(page_url, str)
            parsed = urlsplit(page_url)
            assert parsed.scheme == "http"
            assert parsed.hostname == "fixture-origin"
            assert parsed.port == 8080
            assert (FIXTURE_ROOT / parsed.path.lstrip("/")).is_file()


def test_baseline_contains_twelve_unique_listings_and_a_cross_page_duplicate() -> None:
    manifest = load_manifest()
    pages = manifest["scenarios"]["baseline"]["searchPages"]
    discovered: list[str] = []

    for page_url in pages:
        html = (FIXTURE_ROOT / urlsplit(page_url).path.lstrip("/")).read_text(encoding="utf-8")
        discovered.extend(re.findall(r'data-source-listing-id="([^"]+)"', html))

    assert len(set(discovered)) >= 12
    assert len(discovered) > len(set(discovered))


def test_every_discovered_detail_page_exists_in_the_fixture_corpus() -> None:
    for search_page in (FIXTURE_ROOT / "search").glob("*.html"):
        html = search_page.read_text(encoding="utf-8")
        for href in re.findall(r'href="(/listings/[^"]+\.html)"', html):
            assert (FIXTURE_ROOT / href.lstrip("/")).is_file(), f"Missing detail fixture for {href}"


def test_detail_corpus_has_arabic_css_fallback_and_owned_media() -> None:
    details = list((FIXTURE_ROOT / "listings").glob("*.html"))
    corpus = "\n".join(path.read_text(encoding="utf-8") for path in details)

    assert len(details) >= 12
    assert re.search(r"[\u0600-\u06ff]", corpus)
    assert 'data-extraction-path="css"' in corpus
    assert 'application/ld+json' in corpus
    assert (THIRD_PARTY_MEDIA_ROOT / "fixture-suv.jpg").is_file()
    assert (THIRD_PARTY_MEDIA_ROOT / "fixture-sedan.jpg").is_file()
    assert (THIRD_PARTY_MEDIA_ROOT / "PROVENANCE.md").is_file()


def test_failure_scenario_covers_expected_failure_classes() -> None:
    manifest = load_manifest()
    failure_types = set(manifest["scenarios"]["failures"]["expectedFailures"])

    assert failure_types == {"malformed-json-ld", "unsupported-units", "blocked", "timeout", "not-found"}
