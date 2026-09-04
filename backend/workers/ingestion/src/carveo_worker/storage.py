from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Protocol

from botocore.exceptions import BotoCoreError, ClientError


@dataclass(frozen=True)
class StoredObject:
    data: bytes
    media_type: str
    etag: str


class ObjectStorage(Protocol):
    async def put_if_absent(self, key: str, data: bytes, media_type: str) -> None: ...

    async def open(self, key: str) -> StoredObject | None: ...

    async def delete_many(self, keys: list[str]) -> None: ...


class ObjectStorageError(RuntimeError):
    pass


class S3ObjectStorage:
    def __init__(
        self,
        *,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        region: str = "us-east-1",
    ) -> None:
        import boto3

        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )
        self._bucket = bucket

    async def put_if_absent(self, key: str, data: bytes, media_type: str) -> None:
        try:
            if await asyncio.to_thread(self._exists, key):
                return
            await asyncio.to_thread(
                self._client.put_object,
                Bucket=self._bucket,
                Key=key,
                Body=data,
                ContentType=media_type,
            )
        except (BotoCoreError, ClientError) as exc:
            raise ObjectStorageError("object_write_failed") from exc

    async def open(self, key: str) -> StoredObject | None:
        try:
            return await asyncio.to_thread(self._open_sync, key)
        except (BotoCoreError, ClientError) as exc:
            raise ObjectStorageError("object_read_failed") from exc

    async def delete_many(self, keys: list[str]) -> None:
        if not keys:
            return
        try:
            await asyncio.to_thread(
                self._client.delete_objects,
                Bucket=self._bucket,
                Delete={"Objects": [{"Key": key} for key in keys], "Quiet": True},
            )
        except (BotoCoreError, ClientError) as exc:
            raise ObjectStorageError("object_delete_failed") from exc

    def _exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            if _is_missing(exc):
                return False
            raise
        return True

    def _open_sync(self, key: str) -> StoredObject | None:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
        except ClientError as exc:
            if _is_missing(exc):
                return None
            raise
        data = response["Body"].read()
        etag = key.rsplit("/", 1)[-1].split(".", 1)[0]
        return StoredObject(data=data, media_type=response["ContentType"], etag=etag)


def _is_missing(exc: ClientError) -> bool:
    status = exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode")
    code = exc.response.get("Error", {}).get("Code")
    return status == 404 or code in {"404", "NoSuchKey", "NotFound"}
