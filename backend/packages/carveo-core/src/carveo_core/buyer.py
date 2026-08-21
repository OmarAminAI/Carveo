from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from carveo_core.buyer_contracts import (
    AnonymousWorkspaceMergeRequest,
    BuyerWorkspace,
    Conversation,
    ConversationCreate,
    ConversationSummary,
    ConversationTurnCreate,
    SavedSearch,
    SavedSearchUpsert,
    WorkspaceMergeResponse,
)


class UnknownListingError(ValueError):
    def __init__(self, listing_public_ids: Sequence[str]) -> None:
        self.listing_public_ids = tuple(dict.fromkeys(listing_public_ids))
        super().__init__(f"Unknown listing IDs: {', '.join(self.listing_public_ids)}")


class OwnedResourceNotFound(LookupError):
    """A buyer-owned resource is absent or belongs to another buyer."""


class BuyerWorkspaceRepository(Protocol):
    async def get_workspace(self, clerk_user_id: str) -> BuyerWorkspace: ...

    async def merge_anonymous(
        self,
        clerk_user_id: str,
        payload: AnonymousWorkspaceMergeRequest,
    ) -> WorkspaceMergeResponse: ...

    async def add_shortlist(self, clerk_user_id: str, listing_public_id: str) -> BuyerWorkspace: ...

    async def remove_shortlist(self, clerk_user_id: str, listing_public_id: str) -> BuyerWorkspace: ...

    async def replace_comparison(self, clerk_user_id: str, listing_public_ids: list[str]) -> BuyerWorkspace: ...

    async def upsert_saved_search(self, clerk_user_id: str, payload: SavedSearchUpsert) -> SavedSearch: ...

    async def delete_saved_search(self, clerk_user_id: str, saved_search_id: UUID) -> bool: ...

    async def list_conversations(self, clerk_user_id: str) -> list[ConversationSummary]: ...

    async def create_conversation(self, clerk_user_id: str, payload: ConversationCreate) -> Conversation: ...

    async def get_conversation(self, clerk_user_id: str, conversation_id: UUID) -> Conversation | None: ...

    async def append_turn(
        self,
        clerk_user_id: str,
        conversation_id: UUID,
        payload: ConversationTurnCreate,
    ) -> Conversation | None: ...

