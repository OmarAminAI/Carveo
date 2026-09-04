from __future__ import annotations

from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from carveo_core.ingestion_contracts import (
    CrawlRunSummary,
    ListingReference,
    NormalizedListing,
    SourceQuery,
    UtcDateTime,
)


class IngestionModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CreateRun(IngestionModel):
    source_id: UUID
    query: SourceQuery
    trigger: Literal["manual", "scheduled"]
    correlation_key: str = Field(min_length=1, max_length=240)
    adapter_version: str = Field(min_length=1, max_length=40)
    parser_version: str = Field(min_length=1, max_length=40)
    queued_at: UtcDateTime


class ListingWriteOutcome(IngestionModel):
    outcome: Literal["created", "updated", "unchanged", "restored"]
    listing_id: UUID
    public_id: str
    price_observation_created: bool
    obsolete_media_storage_keys: list[str] = Field(default_factory=list)


class LifecycleSummary(IngestionModel):
    missing_count: int = Field(ge=0)
    removed_count: int = Field(ge=0)


class PurgeSummary(IngestionModel):
    deleted_listing_count: int = Field(ge=0)
    deleted_artifact_count: int = Field(ge=0)
    deleted_run_count: int = Field(ge=0)
    storage_keys: list[str]


class CachedPhotoWrite(IngestionModel):
    position: int = Field(ge=0)
    source_url: str = Field(min_length=1, max_length=2048)
    provenance: Literal["fixture", "approved"]
    source_media_id: str | None = Field(default=None, max_length=160)
    storage_key: str = Field(min_length=1, max_length=512)
    content_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    media_type: Literal["image/jpeg", "image/png", "image/webp", "image/gif"]
    byte_size: int = Field(gt=0, le=10 * 1024 * 1024)


class PhotoSwapResult(IngestionModel):
    outcome: Literal["updated", "unchanged"]
    photo_ids: list[UUID]
    obsolete_storage_keys: list[str]


class IngestionRepository(Protocol):
    async def create_run(self, command: CreateRun) -> CrawlRunSummary: ...

    async def claim_run(self, run_id: UUID, *, started_at: datetime) -> CrawlRunSummary: ...

    async def record_item(self, run_id: UUID, reference: ListingReference, *, identity_key: str) -> UUID: ...

    async def upsert_listing(self, run_id: UUID, listing: NormalizedListing) -> ListingWriteOutcome: ...

    async def reconcile_absent(self, run_id: UUID, *, now: datetime) -> LifecycleSummary: ...

    async def finalize_run(
        self,
        run_id: UUID,
        *,
        discovery_complete: bool,
        finished_at: datetime,
    ) -> CrawlRunSummary: ...

    async def mark_failed(self, run_id: UUID, *, error_code: str, finished_at: datetime) -> CrawlRunSummary: ...

    async def purge_due(self, now: datetime) -> PurgeSummary: ...
