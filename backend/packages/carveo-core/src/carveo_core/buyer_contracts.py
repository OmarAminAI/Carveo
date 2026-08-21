from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import ConfigDict, Field, model_validator

from carveo_core.contracts import ContractModel, to_camel

ListingPublicId = Annotated[str, Field(min_length=1, max_length=160)]
SavedSearchLabel = Annotated[str, Field(min_length=1, max_length=120)]
SavedSearchQuery = Annotated[str, Field(min_length=1, max_length=2000)]
ConversationTitle = Annotated[str, Field(min_length=1, max_length=160)]
ConversationClientId = Annotated[str, Field(min_length=1, max_length=100)]
TurnContent = Annotated[str, Field(min_length=1, max_length=8000)]


class BuyerContractModel(ContractModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )


class SavedSearch(BuyerContractModel):
    id: UUID
    label: SavedSearchLabel
    query: SavedSearchQuery
    created_at: datetime
    updated_at: datetime


class ConversationSummary(BuyerContractModel):
    id: UUID
    title: ConversationTitle
    status: Literal["active", "archived"]
    updated_at: datetime


class ConversationTurn(BuyerContractModel):
    id: UUID
    sequence: int = Field(ge=0)
    role: Literal["buyer", "assistant"]
    content: TurnContent
    created_at: datetime


class Conversation(ConversationSummary):
    client_id: ConversationClientId
    interpreted_intent: dict[str, object] = Field(default_factory=dict)
    created_at: datetime
    turns: list[ConversationTurn] = Field(default_factory=list)


class BuyerWorkspace(BuyerContractModel):
    shortlist_listing_ids: list[ListingPublicId] = Field(default_factory=list)
    comparison_listing_ids: list[ListingPublicId] = Field(default_factory=list)
    saved_searches: list[SavedSearch] = Field(default_factory=list)
    conversations: list[ConversationSummary] = Field(default_factory=list)
    anonymous_merged_at: datetime | None = None


class AnonymousWorkspaceMergeRequest(BuyerContractModel):
    shortlist_listing_ids: list[ListingPublicId] = Field(default_factory=list)
    comparison_listing_ids: list[ListingPublicId] = Field(default_factory=list, max_length=4)
    saved_searches: list[SavedSearchUpsert] = Field(default_factory=list)
    conversations: list[ConversationCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_unique_comparison_listing_ids(self) -> AnonymousWorkspaceMergeRequest:
        if len(self.comparison_listing_ids) != len(set(self.comparison_listing_ids)):
            raise ValueError("comparisonListingIds must contain unique IDs")
        return self


class WorkspaceMergeResponse(BuyerContractModel):
    workspace: BuyerWorkspace
    merged: bool
    ignored_listing_ids: list[ListingPublicId] = Field(default_factory=list)


class ComparisonUpdate(BuyerContractModel):
    listing_ids: list[ListingPublicId] = Field(max_length=4)

    @model_validator(mode="after")
    def validate_unique_listing_ids(self) -> ComparisonUpdate:
        if len(self.listing_ids) != len(set(self.listing_ids)):
            raise ValueError("listingIds must contain unique IDs")
        return self


class SavedSearchUpsert(BuyerContractModel):
    label: SavedSearchLabel
    query: SavedSearchQuery


class ConversationCreate(BuyerContractModel):
    client_id: ConversationClientId
    title: ConversationTitle
    interpreted_intent: dict[str, object] = Field(default_factory=dict)
    turns: list[ConversationTurnCreate] = Field(default_factory=list)


class ConversationTurnCreate(BuyerContractModel):
    role: Literal["buyer", "assistant"]
    content: TurnContent
