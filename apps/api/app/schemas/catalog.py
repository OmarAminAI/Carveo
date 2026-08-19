from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ListingFilters(BaseModel):
    market: str = "AE"
    query: str | None = None
    make: str | None = None
    model: str | None = None
    body_type: str | None = None
    year_min: int | None = None
    year_max: int | None = None
    price_max: int | None = None
    mileage_max_km: int | None = None
    specs: str | None = None
    seller_type: str | None = None
    sort: Literal["best_deal", "price_low", "price_high", "mileage_low", "newest"] = "best_deal"
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=12, ge=1, le=24)


class ConditionEvidence(BaseModel):
    claim: str
    evidence: str | None = None
    confidence: float = Field(ge=0, le=1)


class CatalogueListing(BaseModel):
    id: str
    market: str
    source_id: str
    source_name: str
    source_url: HttpUrl
    source_status: str = "fixture"
    title: str
    make: str
    model: str
    trim: str | None = None
    body_type: str
    price: int
    currency: str = "AED"
    typical_price: int | None = None
    deal_label: Literal["Great deal", "Good deal", "Fair price", "Verify price"] = "Fair price"
    deal_difference: int | None = None
    year: int
    mileage_km: int
    city: str
    seller_type: str
    regional_specs: str | None = None
    color: str | None = None
    warranty: bool = False
    condition: list[ConditionEvidence] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    photos: list[str] = Field(default_factory=list)
    first_seen_at: datetime
    last_seen_at: datetime
    freshness_hours: int = 0


class ListingPage(BaseModel):
    items: list[CatalogueListing]
    total: int
    page: int
    page_size: int
    available_filters: dict[str, list[str]]


class MarketResponse(BaseModel):
    code: str
    name: str
    currency: str
    launched: bool
    source_count: int


class CompareRequest(BaseModel):
    listing_ids: list[str] = Field(min_length=2, max_length=4)


class CompareResponse(BaseModel):
    listings: list[CatalogueListing]


class SavedSearchInput(BaseModel):
    profile_id: str = Field(min_length=16, max_length=80)
    name: str = Field(min_length=1, max_length=120)
    query: dict[str, str | int | bool | None] = Field(default_factory=dict)
    priority_refresh: bool = True


class SavedSearchResponse(SavedSearchInput):
    id: str
