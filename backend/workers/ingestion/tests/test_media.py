from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import httpx
import pytest
from carveo_core.ingestion import PhotoSwapResult
from carveo_core.ingestion_contracts import NormalizedPhoto
from carveo_worker.media import MediaCache
from carveo_worker.storage import ObjectStorageError, StoredObject

pytestmark = pytest.mark.anyio

NOW = datetime(2026, 9, 4, 12, 0, tzinfo=UTC)
LISTING_ID = UUID("00000000-0000-0000-0000-000000000201")
PHOTO_ID = UUID("00000000-0000-0000-0000-000000000202")


class MemoryStorage:
    def __init__(self) -> None:
        self.objects: dict[str, StoredObject] = {}
        self.put_calls: list[str] = []

    async def put_if_absent(self, key: str, data: bytes, media_type: str) -> None:
        self.put_calls.append(key)
        self.objects.setdefault(
            key,
            StoredObject(data=data, media_type=media_type, etag=key.split("/")[-1].split(".")[0]),
        )

    async def open(self, key: str) -> StoredObject | None:
        return self.objects.get(key)

    async def delete_many(self, keys: list[str]) -> None:
        for key in keys:
            self.objects.pop(key, None)


class FailingStorage(MemoryStorage):
    async def put_if_absent(self, key: str, data: bytes, media_type: str) -> None:
        raise ObjectStorageError("storage_unavailable")


class OversizedStream(httpx.AsyncByteStream):
    async def __aiter__(self):  # type: ignore[no-untyped-def]
        yield b"x" * 20
        yield b"x" * 20
        raise AssertionError("the downloader read beyond the configured ceiling")


class RecordingPhotoRepository:
    def __init__(self) -> None:
        self.calls = 0
        self.writes: list[object] = []

    async def replace_listing_photos(
        self,
        listing_id: UUID,
        photos: list[object],
        refreshed_at: datetime,
    ) -> PhotoSwapResult:
        self.calls += 1
        self.writes = photos
        return PhotoSwapResult(outcome="updated", photo_ids=[PHOTO_ID], obsolete_storage_keys=["old/key.jpg"])


def photo(url: str) -> NormalizedPhoto:
    return NormalizedPhoto(source_url=url, provenance="fixture")


def image_response(content: bytes = b"jpeg-bytes", *, content_type: str = "image/jpeg") -> httpx.Response:
    return httpx.Response(
        200,
        content=content,
        headers={"content-type": content_type, "content-length": str(len(content))},
    )


async def test_refresh_caches_third_party_bytes_by_hash_and_swaps_only_after_all_downloads() -> None:
    transport = httpx.MockTransport(lambda _: image_response())
    storage = MemoryStorage()
    repository = RecordingPhotoRepository()
    async with httpx.AsyncClient(transport=transport) as http:
        result = await MediaCache(
            http=http,
            storage=storage,
            repository=repository,
            allowed_hosts={"fixture-origin"},
            allowed_schemes={"http"},
        ).refresh(
            LISTING_ID,
            [
                photo("http://fixture-origin/media/front.jpg"),
                photo("http://fixture-origin/media/rear.jpg"),
            ],
            NOW,
        )

    assert result.outcome == "updated"
    assert result.photo_ids == [PHOTO_ID]
    assert result.obsolete_storage_keys == ["old/key.jpg"]
    assert repository.calls == 1
    assert len(storage.objects) == 1
    assert len(storage.put_calls) == 1
    assert [write.position for write in repository.writes] == [0, 1]  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("url", "allowed_schemes", "allowed_hosts"),
    [
        ("file:///private/image.jpg", {"http"}, {"fixture-origin"}),
        ("https://fixture-origin/image.jpg", {"http"}, {"fixture-origin"}),
        ("http://evil.example/image.jpg", {"http"}, {"fixture-origin"}),
        ("http://user:pass@fixture-origin/image.jpg", {"http"}, {"fixture-origin"}),
    ],
)
async def test_disallowed_media_target_fails_before_download(
    url: str,
    allowed_schemes: set[str],
    allowed_hosts: set[str],
) -> None:
    requests = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        return image_response()

    repository = RecordingPhotoRepository()
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        result = await MediaCache(
            http=http,
            storage=MemoryStorage(),
            repository=repository,
            allowed_hosts=allowed_hosts,
            allowed_schemes=allowed_schemes,
        ).refresh(LISTING_ID, [photo(url)], NOW)

    assert result.outcome == "failed"
    assert requests == 0
    assert repository.calls == 0


async def test_redirect_destination_is_revalidated() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "fixture-origin":
            return httpx.Response(302, headers={"location": "http://evil.example/stolen.jpg"})
        return image_response()

    repository = RecordingPhotoRepository()
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        result = await MediaCache(
            http=http,
            storage=MemoryStorage(),
            repository=repository,
            allowed_hosts={"fixture-origin"},
            allowed_schemes={"http"},
        ).refresh(LISTING_ID, [photo("http://fixture-origin/image.jpg")], NOW)

    assert result.outcome == "failed"
    assert repository.calls == 0


@pytest.mark.parametrize(
    "response",
    [
        image_response(content_type="text/html"),
        httpx.Response(200, content=b"x", headers={"content-type": "image/jpeg", "content-length": "10485761"}),
        httpx.Response(200, content=b"x" * 33, headers={"content-type": "image/jpeg"}),
    ],
)
async def test_invalid_type_declared_size_or_streamed_size_preserves_previous_photo_set(
    response: httpx.Response,
) -> None:
    repository = RecordingPhotoRepository()
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: response)) as http:
        result = await MediaCache(
            http=http,
            storage=MemoryStorage(),
            repository=repository,
            allowed_hosts={"fixture-origin"},
            allowed_schemes={"http"},
            max_bytes=32,
        ).refresh(LISTING_ID, [photo("http://fixture-origin/image.jpg")], NOW)

    assert result.outcome == "failed"
    assert repository.calls == 0


async def test_invalid_content_length_is_a_validation_failure() -> None:
    response = httpx.Response(
        200,
        content=b"jpeg-bytes",
        headers={"content-type": "image/jpeg", "content-length": "unknown"},
    )
    repository = RecordingPhotoRepository()
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: response)) as http:
        result = await MediaCache(
            http=http,
            storage=MemoryStorage(),
            repository=repository,
            allowed_hosts={"fixture-origin"},
            allowed_schemes={"http"},
        ).refresh(LISTING_ID, [photo("http://fixture-origin/image.jpg")], NOW)

    assert result.outcome == "failed"
    assert repository.calls == 0


async def test_stream_stops_as_soon_as_the_byte_ceiling_is_crossed() -> None:
    response = httpx.Response(200, stream=OversizedStream(), headers={"content-type": "image/jpeg"})
    repository = RecordingPhotoRepository()
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: response)) as http:
        result = await MediaCache(
            http=http,
            storage=MemoryStorage(),
            repository=repository,
            allowed_hosts={"fixture-origin"},
            allowed_schemes={"http"},
            max_bytes=32,
        ).refresh(LISTING_ID, [photo("http://fixture-origin/image.jpg")], NOW)

    assert result.outcome == "failed"
    assert repository.calls == 0


async def test_storage_failure_preserves_previous_photo_set() -> None:
    repository = RecordingPhotoRepository()
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: image_response())) as http:
        result = await MediaCache(
            http=http,
            storage=FailingStorage(),
            repository=repository,
            allowed_hosts={"fixture-origin"},
            allowed_schemes={"http"},
        ).refresh(LISTING_ID, [photo("http://fixture-origin/image.jpg")], NOW)

    assert result.outcome == "failed"
    assert repository.calls == 0


async def test_image_count_is_bounded_before_any_download() -> None:
    requests = 0

    def handler(_: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        return image_response()

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        result = await MediaCache(
            http=http,
            storage=MemoryStorage(),
            repository=RecordingPhotoRepository(),
            allowed_hosts={"fixture-origin"},
            allowed_schemes={"http"},
            max_images=2,
        ).refresh(
            LISTING_ID,
            [photo(f"http://fixture-origin/{index}.jpg") for index in range(3)],
            NOW,
        )

    assert result.outcome == "failed"
    assert requests == 0
