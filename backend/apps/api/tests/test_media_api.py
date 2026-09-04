from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import UUID

import httpx
import pytest
from carveo_api.main import create_app
from carveo_api.media import MediaAsset
from carveo_core.catalogue import FixtureCatalogueRepository
from carveo_core.fixtures import load_fixture_listings

PHOTO_ID = UUID("00000000-0000-0000-0000-000000000202")


class StubMediaService:
    async def get(self, photo_id: UUID) -> MediaAsset | None:
        if photo_id != PHOTO_ID:
            return None
        return MediaAsset(data=b"third-party-image", media_type="image/jpeg", etag="sha256-etag")


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    app = create_app(
        repository=FixtureCatalogueRepository(load_fixture_listings()),
        media_service=StubMediaService(),
    )
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client


@pytest.mark.anyio
async def test_media_proxy_returns_bytes_type_etag_and_immutable_cache_headers(client: httpx.AsyncClient) -> None:
    response = await client.get(f"/api/v1/media/{PHOTO_ID}")

    assert response.status_code == 200
    assert response.content == b"third-party-image"
    assert response.headers["content-type"] == "image/jpeg"
    assert response.headers["etag"] == '"sha256-etag"'
    assert response.headers["cache-control"] == "public, max-age=31536000, immutable"


@pytest.mark.anyio
async def test_media_proxy_returns_not_modified_for_matching_etag(client: httpx.AsyncClient) -> None:
    response = await client.get(f"/api/v1/media/{PHOTO_ID}", headers={"If-None-Match": '"sha256-etag"'})

    assert response.status_code == 304
    assert response.content == b""


@pytest.mark.anyio
async def test_unknown_photo_is_sanitized_problem_without_storage_details(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/media/00000000-0000-0000-0000-000000000999")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert "storage_key" not in response.text
    assert "minio" not in response.text.lower()


@pytest.mark.anyio
async def test_media_route_rejects_non_uuid_identifier(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/media/not-a-uuid")

    assert response.status_code == 422


def test_media_openapi_contract_declares_binary_image_responses() -> None:
    app = create_app(
        repository=FixtureCatalogueRepository(load_fixture_listings()),
        media_service=StubMediaService(),
    )

    response_content = app.openapi()["paths"]["/api/v1/media/{photo_id}"]["get"]["responses"]["200"]["content"]

    assert set(response_content) == {"image/gif", "image/jpeg", "image/png", "image/webp"}
    assert all(schema == {"schema": {"format": "binary", "type": "string"}} for schema in response_content.values())
