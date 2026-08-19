from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class SearchIntent(BaseModel):
    market: str | None = None
    city: str | None = None
    make: str | None = None
    models: list[str] = Field(default_factory=list)
    body_types: list[str] = Field(default_factory=list)
    year_min: int | None = Field(default=None, ge=1990, le=2030)
    year_max: int | None = Field(default=None, ge=1990, le=2030)
    budget_max: int | None = Field(default=None, ge=0)
    currency: str | None = None
    mileage_max_km: int | None = Field(default=None, ge=0)
    colors: list[str] = Field(default_factory=list)
    specifications: list[str] = Field(default_factory=list)
    condition_preferences: list[str] = Field(default_factory=list)
    broad_model_search: bool = False
    budget_optional: bool = False


class IntentState(BaseModel):
    intent: SearchIntent
    ready: bool
    missing_fields: list[str]
    next_question: str | None


class CreateSessionResponse(BaseModel):
    session_id: str
    intent_state: IntentState


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=1_500)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class SendMessageResponse(BaseModel):
    session_id: str
    message: ChatMessage
    intent_state: IntentState


class VehicleListing(BaseModel):
    id: str
    source_id: str
    source_name: str
    source_url: HttpUrl
    title: str
    price: int
    currency: str
    city: str
    make: str
    model: str
    year: int
    mileage_km: int
    color: str | None = None
    specifications: list[str] = Field(default_factory=list)
    seller_type: str
    warranty: bool = False
    condition_signals: list[str] = Field(default_factory=list)
    freshness_days: int = 0


class RankedMatch(BaseModel):
    listing: VehicleListing
    score: float
    score_components: dict[str, float]
    reasons: list[str]
    warnings: list[str]


class SearchResultsResponse(BaseModel):
    session_id: str
    intent: SearchIntent
    matches: list[RankedMatch]

