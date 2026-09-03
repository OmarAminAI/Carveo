from __future__ import annotations

from typing import Protocol

from carveo_core.ingestion_contracts import ListingReference, RawListing, RejectedListing, SourceQuery
from pydantic import BaseModel, ConfigDict, Field


class DiscoveryResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    references: list[ListingReference]
    visited_pages: list[str]
    discovery_complete: bool
    error_code: str | None = Field(default=None, max_length=80)


class SourceAdapter(Protocol):
    async def discover(self, query: SourceQuery) -> DiscoveryResult: ...

    async def extract(self, reference: ListingReference) -> RawListing | RejectedListing: ...
