from collections.abc import AsyncIterator

import httpx
import pytest
from carveo_api.main import create_app
from carveo_core.catalogue import FixtureCatalogueRepository
from carveo_core.contracts import ListingPage, ListingQuery
from carveo_core.fixtures import load_fixture_listings


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    app = create_app(
        repository=FixtureCatalogueRepository(load_fixture_listings()),
        readiness_check=lambda: ready(),
    )
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client


async def ready() -> bool:
    return True


@pytest.mark.anyio
async def test_health_and_readiness_are_distinct(client: httpx.AsyncClient) -> None:
    health = await client.get("/health", headers={"X-Request-ID": "test-request-id"})
    readiness = await client.get("/ready")

    assert health.json() == {"status": "alive"}
    assert health.headers["X-Request-ID"] == "test-request-id"
    assert readiness.json() == {"status": "ready"}


@pytest.mark.anyio
async def test_metrics_are_scrapeable_without_expanding_the_public_contract(client: httpx.AsyncClient) -> None:
    await client.get("/health")

    metrics = await client.get("/metrics")
    schema = await client.get("/openapi.json")

    assert metrics.status_code == 200
    assert metrics.headers["content-type"].startswith("text/plain")
    assert "carveo_api_http_requests_total" in metrics.text
    assert "/metrics" not in schema.json()["paths"]


@pytest.mark.anyio
async def test_repeated_filters_use_camel_case_contract(client: httpx.AsyncClient) -> None:
    response = await client.get(
        "/api/v1/listings",
        params=[("make", "Toyota"), ("make", "Nissan"), ("bodyType", "SUV"), ("pageSize", "12")],
    )

    assert response.status_code == 200
    body = response.json()
    assert body["items"]
    assert all(item["make"] in {"Toyota", "Nissan"} for item in body["items"])
    assert body["pageSize"] == 12


@pytest.mark.anyio
async def test_detail_compare_and_missing_problem(client: httpx.AsyncClient) -> None:
    listing_id = "cv-toyota-rav4-2021-02"
    detail = await client.get(f"/api/v1/listings/{listing_id}")
    comparison = await client.post("/api/v1/compare", json={"listingIds": [listing_id, "missing"]})
    missing = await client.get("/api/v1/listings/missing")

    assert detail.json()["id"] == listing_id
    assert comparison.json()["missingIds"] == ["missing"]
    assert missing.status_code == 404
    assert missing.headers["content-type"].startswith("application/problem+json")
    assert missing.json()["type"] == "https://carveo.local/problems/not-found"


@pytest.mark.anyio
async def test_invalid_range_is_problem_response(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/listings?priceMin=200000&priceMax=100000")

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")


@pytest.mark.anyio
async def test_unexpected_failures_are_sanitized() -> None:
    class FailingRepository(FixtureCatalogueRepository):
        async def search(self, query: ListingQuery) -> ListingPage:
            raise RuntimeError("sensitive internal detail")

    app = create_app(repository=FailingRepository(load_fixture_listings()))
    transport = httpx.ASGITransport(app=app, raise_app_exceptions=False)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        response = await test_client.get("/api/v1/listings")

    assert response.status_code == 500
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["type"] == "https://carveo.local/problems/internal-error"
    assert "sensitive" not in response.text
