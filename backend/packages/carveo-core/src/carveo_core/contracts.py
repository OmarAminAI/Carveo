from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part.capitalize() for part in tail)


class ContractModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ConditionEvidence(ContractModel):
    kind: Literal["positive", "warning", "unknown"]
    label: str
    detail: str
    source_claim: str | None = None


class PriceObservation(ContractModel):
    observed_at: datetime
    price: int = Field(ge=0)


class DuplicateOffer(ContractModel):
    source: str
    price: int = Field(ge=0)
    url: str


class SourceAttribution(ContractModel):
    name: str
    listing_url: str
    status: Literal["Fixture", "Approved"]


class DealPosition(ContractModel):
    label: Literal["Below typical", "Near typical", "Above typical", "Limited data"]
    typical_price: int | None = None
    difference_amount: int | None = None
    difference_percent: float | None = None
    sample_size: int = Field(ge=0)


class Listing(ContractModel):
    id: str
    market: Literal["ae"]
    title: str
    make: str
    model: str
    trim: str
    year: int
    price: int = Field(ge=0)
    currency: Literal["AED"]
    mileage_km: int = Field(ge=0)
    city: Literal["Dubai", "Abu Dhabi", "Sharjah", "Ajman"]
    body_type: Literal["SUV", "Sedan", "Coupe", "Hatchback", "Pickup", "Convertible"]
    specifications: Literal["GCC", "American", "European", "Japanese"]
    seller_type: Literal["Dealer", "Private"]
    source: SourceAttribution
    description: str
    features: list[str]
    photos: list[str] = Field(min_length=1)
    first_seen_at: datetime
    last_seen_at: datetime
    condition_evidence: list[ConditionEvidence]
    price_history: list[PriceObservation]
    duplicate_offers: list[DuplicateOffer]
    deal_position: DealPosition | None = None


class FixtureSeed(ContractModel):
    id: str
    make: str
    model: str
    trim: str
    year: int
    price: int
    mileage_km: int
    city: str
    body_type: str
    specifications: str
    seller_type: str


class ListingPage(ContractModel):
    items: list[Listing]
    total: int
    page: int
    page_size: int
    page_count: int


class ListingQuery(ContractModel):
    market: Literal["ae"] = "ae"
    q: str = ""
    make: list[str] = Field(default_factory=list)
    model: list[str] = Field(default_factory=list)
    body_type: list[str] = Field(default_factory=list)
    year_min: int | None = Field(default=None, ge=1900)
    year_max: int | None = Field(default=None, ge=1900)
    price_min: int | None = Field(default=None, ge=0)
    price_max: int | None = Field(default=None, ge=0)
    mileage_max: int | None = Field(default=None, ge=0)
    specifications: list[str] = Field(default_factory=list)
    seller_type: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    city: list[str] = Field(default_factory=list)
    sort: Literal["best-match", "best-deal", "newest", "lowest-price", "lowest-mileage"] = "best-match"
    page: int = Field(default=1, ge=1)
    page_size: Literal[12, 24, 48] = 12

    @model_validator(mode="after")
    def validate_ranges(self) -> "ListingQuery":
        ranges = (
            ("yearMin", self.year_min, "yearMax", self.year_max),
            ("priceMin", self.price_min, "priceMax", self.price_max),
        )
        for minimum_name, minimum, maximum_name, maximum in ranges:
            if minimum is not None and maximum is not None and minimum > maximum:
                raise ValueError(f"{minimum_name} must be less than or equal to {maximum_name}")
        return self


class CompareRequest(ContractModel):
    listing_ids: list[str] = Field(min_length=1, max_length=4)


class CompareResponse(ContractModel):
    items: list[Listing]
    missing_ids: list[str]


class Market(ContractModel):
    code: Literal["ae"]
    locale: Literal["en-ae"]
    name: Literal["United Arab Emirates"]
    currency: Literal["AED"]


class ModelMarketSummary(ContractModel):
    make: str
    model: str
    active_listings: int
    median_price: int
    min_price: int
    max_price: int
    min_mileage: int
    max_mileage: int
    last_updated_at: datetime


class ModelInsights(ContractModel):
    summary: ModelMarketSummary
    listings: list[Listing]
