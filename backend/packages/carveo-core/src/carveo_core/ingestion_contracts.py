from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, model_validator


def _require_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() != timedelta(0):
        raise ValueError("timestamp must use UTC")
    return value


UtcDateTime = Annotated[datetime, AfterValidator(_require_utc)]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partially_completed"
    FAILED = "failed"


class SourceProfile(StrictModel):
    id: UUID
    key: str = Field(min_length=1, max_length=80)
    market: str = Field(min_length=2, max_length=8)
    authorization_status: Literal["fixture", "pending", "approved", "blocked"]
    enabled: bool
    environment_allowlist: list[Literal["development", "test", "production"]]
    allowed_hosts: list[str]
    allowed_schemes: list[Literal["http", "https"]]
    terms_reviewed_at: UtcDateTime | None = None
    adapter_version: str = Field(min_length=1, max_length=40)
    parser_version: str = Field(min_length=1, max_length=40)
    concurrency_limit: int = Field(ge=1, le=32)
    rate_limit_per_minute: int = Field(ge=1, le=10_000)
    killed_at: UtcDateTime | None = None
    kill_reason: str | None = Field(default=None, max_length=240)


class SourceQuery(StrictModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    market: Literal["ae"] = "ae"
    query_key: str = Field(min_length=1, max_length=120)
    fixture_scenario: str = Field(min_length=1, max_length=80)


class ListingReference(StrictModel):
    source_key: str = Field(min_length=1, max_length=80)
    source_listing_id: str | None = Field(default=None, min_length=1, max_length=160)
    canonical_url: str = Field(min_length=1, max_length=2048)
    discovered_at: UtcDateTime
    search_page_key: str = Field(min_length=1, max_length=160)


class RawPhoto(StrictModel):
    source_url: str = Field(min_length=1, max_length=2048)
    source_media_id: str | None = Field(default=None, max_length=160)


class RawConditionClaim(StrictModel):
    kind: Literal["positive", "warning", "unknown"]
    label: str = Field(min_length=1, max_length=160)
    detail: str = Field(min_length=1, max_length=4000)
    source_claim: str | None = Field(default=None, max_length=4000)
    confidence: float | None = Field(default=None, ge=0, le=1)


class RawListing(StrictModel):
    reference: ListingReference
    title: str | None = None
    make: str | None = None
    model: str | None = None
    trim: str | None = None
    year: str | None = None
    price: str | None = None
    currency: str | None = None
    mileage: str | None = None
    city: str | None = None
    body_type: str | None = None
    specifications: str | None = None
    seller_type: str | None = None
    description: str = ""
    features: list[str] = Field(default_factory=list)
    photos: list[RawPhoto] = Field(default_factory=list)
    condition_claims: list[RawConditionClaim] = Field(default_factory=list)
    source_sold: bool = False
    extraction_path: Literal["json-ld", "css"]
    extracted_at: UtcDateTime


class NormalizedPhoto(StrictModel):
    source_url: str = Field(min_length=1, max_length=2048)
    provenance: Literal["fixture", "approved"]
    source_media_id: str | None = Field(default=None, max_length=160)


class NormalizedConditionEvidence(StrictModel):
    kind: Literal["positive", "warning", "unknown"]
    label: str = Field(min_length=1, max_length=160)
    detail: str = Field(min_length=1, max_length=4000)
    source_claim: str | None = Field(default=None, max_length=4000)
    confidence: float | None = Field(default=None, ge=0, le=1)


class NormalizedListing(StrictModel):
    reference: ListingReference
    market: Literal["ae"]
    title: str = Field(min_length=1, max_length=240)
    make: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    trim: str = Field(min_length=1, max_length=120)
    year: int = Field(ge=1900, le=2100)
    price: int = Field(ge=0)
    currency: Literal["AED"]
    mileage_km: int = Field(ge=0)
    city: Literal["Dubai", "Abu Dhabi", "Sharjah", "Ajman"]
    body_type: Literal["SUV", "Sedan", "Coupe", "Hatchback", "Pickup", "Convertible"]
    specifications: Literal["GCC", "American", "European", "Japanese"]
    seller_type: Literal["Dealer", "Private"]
    description: str
    features: list[str]
    photos: list[NormalizedPhoto]
    condition_evidence: list[NormalizedConditionEvidence]
    source_sold: bool
    original_values: dict[str, str]
    extracted_at: UtcDateTime


class RejectedListing(StrictModel):
    reference: ListingReference
    error_code: str = Field(min_length=1, max_length=80)
    detail: str = Field(min_length=1, max_length=400)


class CrawlRunSummary(StrictModel):
    id: UUID
    source_key: str
    trigger: Literal["manual", "scheduled"]
    status: RunStatus
    discovery_complete: bool
    counters: dict[str, int]
    queued_at: UtcDateTime
    started_at: UtcDateTime | None = None
    finished_at: UtcDateTime | None = None
    error_code: str | None = None

    @model_validator(mode="after")
    def validate_terminal_timestamp(self) -> CrawlRunSummary:
        if self.status in {RunStatus.COMPLETED, RunStatus.PARTIAL, RunStatus.FAILED} and self.finished_at is None:
            raise ValueError("terminal runs require finished_at")
        return self


class CrawlRunItemResult(StrictModel):
    run_item_id: UUID
    outcome: Literal["created", "updated", "unchanged", "restored", "rejected", "failed"]
    listing_public_id: str | None = None
    error_code: str | None = None


class MediaCacheResult(StrictModel):
    listing_id: UUID
    outcome: Literal["updated", "unchanged", "failed"]
    photo_ids: list[UUID]
    obsolete_storage_keys: list[str]
