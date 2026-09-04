from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from botocore.exceptions import ClientError
from carveo_core.models import ListingPhoto
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@dataclass(frozen=True)
class MediaAsset:
    data: bytes
    media_type: str
    etag: str


class MediaService(Protocol):
    async def get(self, photo_id: UUID) -> MediaAsset | None: ...


class DatabaseMediaService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], reader: ObjectReader) -> None:
        self._session_factory = session_factory
        self._reader = reader

    async def get(self, photo_id: UUID) -> MediaAsset | None:
        async with self._session_factory() as session:
            record = await session.scalar(select(ListingPhoto).where(ListingPhoto.id == photo_id))
        if record is None or record.storage_key is None:
            return None
        return await self._reader.open(record.storage_key)


class ObjectReader(Protocol):
    async def open(self, key: str) -> MediaAsset | None: ...


class S3ObjectReader:
    def __init__(self, *, endpoint_url: str, access_key: str, secret_key: str, bucket: str) -> None:
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket = bucket

    async def open(self, key: str) -> MediaAsset | None:
        return await asyncio.to_thread(self._open_sync, key)

    def _open_sync(self, key: str) -> MediaAsset | None:
        import boto3

        client = boto3.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            region_name="us-east-1",
        )
        try:
            response = client.get_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
            code = exc.response.get("Error", {}).get("Code")
            if status == 404 or code in {"404", "NoSuchKey", "NotFound"}:
                return None
            raise
        return MediaAsset(
            data=response["Body"].read(),
            media_type=response["ContentType"],
            etag=key.rsplit("/", 1)[-1].split(".", 1)[0],
        )
