from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from urllib.parse import urljoin, urlsplit
from uuid import UUID

import httpx
from carveo_core.ingestion import CachedPhotoWrite, PhotoSwapResult
from carveo_core.ingestion_contracts import MediaCacheResult, NormalizedPhoto

from carveo_worker.storage import ObjectStorage, ObjectStorageError

ALLOWED_MEDIA_TYPES = {
    "image/gif": "gif",
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


class PhotoRepository(Protocol):
    async def replace_listing_photos(
        self,
        listing_id: UUID,
        photos: list[CachedPhotoWrite],
        refreshed_at: datetime,
    ) -> PhotoSwapResult: ...


class MediaValidationError(ValueError):
    pass


@dataclass(frozen=True)
class _DownloadedPhoto:
    write: CachedPhotoWrite
    data: bytes


class MediaCache:
    def __init__(
        self,
        *,
        http: httpx.AsyncClient,
        storage: ObjectStorage,
        repository: PhotoRepository,
        allowed_hosts: set[str],
        allowed_schemes: set[str],
        max_images: int = 20,
        max_bytes: int = 10 * 1024 * 1024,
        max_redirects: int = 3,
    ) -> None:
        self._http = http
        self._storage = storage
        self._repository = repository
        self._allowed_hosts = {host.lower() for host in allowed_hosts}
        self._allowed_schemes = {scheme.lower() for scheme in allowed_schemes}
        self._max_images = max_images
        self._max_bytes = max_bytes
        self._max_redirects = max_redirects

    async def refresh(
        self,
        listing_id: UUID,
        photos: Sequence[NormalizedPhoto],
        refreshed_at: datetime,
    ) -> MediaCacheResult:
        if len(photos) > self._max_images:
            return _failed(listing_id)
        try:
            writes = [
                await self._download(position, photo)
                for position, photo in enumerate(photos)
            ]
            uploaded: set[str] = set()
            for downloaded in writes:
                if downloaded.write.storage_key in uploaded:
                    continue
                uploaded.add(downloaded.write.storage_key)
                await self._storage.put_if_absent(
                    downloaded.write.storage_key,
                    downloaded.data,
                    downloaded.write.media_type,
                )
            persisted = [downloaded.write for downloaded in writes]
            swap = await self._repository.replace_listing_photos(listing_id, persisted, refreshed_at)
        except (MediaValidationError, ObjectStorageError, httpx.HTTPError, OSError):
            return _failed(listing_id)
        return MediaCacheResult(
            listing_id=listing_id,
            outcome=swap.outcome,
            photo_ids=swap.photo_ids,
            obsolete_storage_keys=swap.obsolete_storage_keys,
        )

    async def _download(self, position: int, photo: NormalizedPhoto) -> _DownloadedPhoto:
        url = photo.source_url
        for redirect in range(self._max_redirects + 1):
            self._validate_url(url)
            async with self._http.stream("GET", url, follow_redirects=False, timeout=20.0) as response:
                if response.is_redirect:
                    location = response.headers.get("location")
                    if not location or redirect == self._max_redirects:
                        raise MediaValidationError("redirect_invalid")
                    url = urljoin(url, location)
                    continue
                if response.status_code != 200:
                    raise MediaValidationError("download_failed")
                media_type = response.headers.get("content-type", "").split(";", 1)[0].lower()
                extension = ALLOWED_MEDIA_TYPES.get(media_type)
                if extension is None:
                    raise MediaValidationError("media_type_invalid")
                self._validate_declared_size(response.headers.get("content-length"))
                data = bytearray()
                async for chunk in response.aiter_bytes():
                    data.extend(chunk)
                    if len(data) > self._max_bytes:
                        raise MediaValidationError("media_too_large")
                if not data:
                    raise MediaValidationError("media_empty")
                content = bytes(data)
                content_hash = hashlib.sha256(content).hexdigest()
                return _DownloadedPhoto(
                    write=CachedPhotoWrite(
                        position=position,
                        source_url=photo.source_url,
                        provenance=photo.provenance,
                        source_media_id=photo.source_media_id,
                        storage_key=f"sha256/{content_hash[:2]}/{content_hash}.{extension}",
                        content_hash=content_hash,
                        media_type=media_type,
                        byte_size=len(content),
                    ),
                    data=content,
                )
        raise MediaValidationError("redirect_invalid")

    def _validate_declared_size(self, value: str | None) -> None:
        if value is None:
            return
        try:
            declared_size = int(value)
        except ValueError as exc:
            raise MediaValidationError("content_length_invalid") from exc
        if declared_size < 0 or declared_size > self._max_bytes:
            raise MediaValidationError("media_too_large")

    def _validate_url(self, url: str) -> None:
        try:
            parsed = urlsplit(url)
            _ = parsed.port
        except ValueError as exc:
            raise MediaValidationError("media_url_invalid") from exc
        if parsed.scheme.lower() not in self._allowed_schemes or not parsed.hostname:
            raise MediaValidationError("media_url_forbidden")
        if parsed.hostname.lower() not in self._allowed_hosts:
            raise MediaValidationError("media_host_forbidden")
        if parsed.username is not None or parsed.password is not None:
            raise MediaValidationError("media_credentials_forbidden")


def _failed(listing_id: UUID) -> MediaCacheResult:
    return MediaCacheResult(
        listing_id=listing_id,
        outcome="failed",
        photo_ids=[],
        obsolete_storage_keys=[],
    )
