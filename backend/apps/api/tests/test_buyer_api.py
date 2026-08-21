from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID

import httpx
import pytest
from carveo_api.auth import AuthenticatedBuyer, AuthenticationError
from carveo_api.main import create_app
from carveo_core.buyer import InvalidSavedSearchQueryError, UnknownListingError
from carveo_core.buyer_contracts import (
    AnonymousWorkspaceMergeRequest,
    BuyerWorkspace,
    Conversation,
    ConversationCreate,
    ConversationSummary,
    ConversationTurn,
    ConversationTurnCreate,
    SavedSearch,
    SavedSearchUpsert,
    WorkspaceMergeResponse,
)
from carveo_core.catalogue import FixtureCatalogueRepository
from carveo_core.fixtures import load_fixture_listings
from starlette.requests import Request

NOW = datetime(2026, 8, 22, 12, tzinfo=UTC)
SAVED_ID = UUID("11111111-1111-4111-8111-111111111111")
CONVERSATION_ID = UUID("22222222-2222-4222-8222-222222222222")
TURN_ID = UUID("33333333-3333-4333-8333-333333333333")


class FakeAuthenticator:
    async def authenticate(self, request: Request) -> AuthenticatedBuyer:
        if request.headers.get("Authorization") != "Bearer verified":
            raise AuthenticationError
        return AuthenticatedBuyer(clerk_user_id="user_clerk_1")


class FakeBuyerRepository:
    def __init__(self) -> None:
        self.users: list[str] = []
        self.workspace = BuyerWorkspace(
            shortlist_listing_ids=["cv-toyota-rav4-2021-02"],
            comparison_listing_ids=[],
            saved_searches=[],
            conversations=[],
        )

    def _owned(self, clerk_user_id: str) -> None:
        self.users.append(clerk_user_id)

    async def get_workspace(self, clerk_user_id: str) -> BuyerWorkspace:
        self._owned(clerk_user_id)
        return self.workspace

    async def merge_anonymous(
        self, clerk_user_id: str, payload: AnonymousWorkspaceMergeRequest
    ) -> WorkspaceMergeResponse:
        self._owned(clerk_user_id)
        return WorkspaceMergeResponse(
            workspace=self.workspace,
            merged=True,
            ignored_listing_ids=["missing-listing"],
        )

    async def add_shortlist(self, clerk_user_id: str, listing_public_id: str) -> BuyerWorkspace:
        self._owned(clerk_user_id)
        if listing_public_id == "missing-listing":
            raise UnknownListingError([listing_public_id])
        return self.workspace

    async def remove_shortlist(self, clerk_user_id: str, listing_public_id: str) -> BuyerWorkspace:
        self._owned(clerk_user_id)
        return self.workspace

    async def replace_comparison(self, clerk_user_id: str, listing_public_ids: list[str]) -> BuyerWorkspace:
        self._owned(clerk_user_id)
        if "missing-listing" in listing_public_ids:
            raise UnknownListingError(["missing-listing"])
        return self.workspace.model_copy(update={"comparison_listing_ids": listing_public_ids})

    async def upsert_saved_search(self, clerk_user_id: str, payload: SavedSearchUpsert) -> SavedSearch:
        self._owned(clerk_user_id)
        if payload.query == "?":
            raise InvalidSavedSearchQueryError
        return SavedSearch(id=SAVED_ID, label=payload.label, query=payload.query, created_at=NOW, updated_at=NOW)

    async def delete_saved_search(self, clerk_user_id: str, saved_search_id: UUID) -> bool:
        self._owned(clerk_user_id)
        return saved_search_id == SAVED_ID

    async def list_conversations(self, clerk_user_id: str) -> list[ConversationSummary]:
        self._owned(clerk_user_id)
        return [ConversationSummary(id=CONVERSATION_ID, title="Family SUV", status="active", updated_at=NOW)]

    async def create_conversation(self, clerk_user_id: str, payload: ConversationCreate) -> Conversation:
        self._owned(clerk_user_id)
        return self._conversation(payload.client_id, payload.title)

    async def get_conversation(self, clerk_user_id: str, conversation_id: UUID) -> Conversation | None:
        self._owned(clerk_user_id)
        return self._conversation("browser-1", "Family SUV") if conversation_id == CONVERSATION_ID else None

    async def append_turn(
        self, clerk_user_id: str, conversation_id: UUID, payload: ConversationTurnCreate
    ) -> Conversation | None:
        self._owned(clerk_user_id)
        if conversation_id != CONVERSATION_ID:
            return None
        conversation = self._conversation("browser-1", "Family SUV")
        return conversation.model_copy(
            update={
                "turns": [
                    ConversationTurn(id=TURN_ID, sequence=0, role=payload.role, content=payload.content, created_at=NOW)
                ]
            }
        )

    @staticmethod
    def _conversation(client_id: str, title: str) -> Conversation:
        return Conversation(
            id=CONVERSATION_ID,
            client_id=client_id,
            title=title,
            status="active",
            interpreted_intent={},
            created_at=NOW,
            updated_at=NOW,
            turns=[],
        )


@pytest.fixture
async def buyer_api() -> AsyncIterator[tuple[httpx.AsyncClient, FakeBuyerRepository]]:
    buyer_repository = FakeBuyerRepository()
    app = create_app(
        repository=FixtureCatalogueRepository(load_fixture_listings()),
        buyer_repository=buyer_repository,
        authenticator=FakeAuthenticator(),
    )
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        yield client, buyer_repository


def verified() -> dict[str, str]:
    return {"Authorization": "Bearer verified"}


@pytest.mark.anyio
async def test_workspace_and_merge_are_authenticated_and_camel_case(
    buyer_api: tuple[httpx.AsyncClient, FakeBuyerRepository],
) -> None:
    client, repository = buyer_api

    missing = await client.get("/api/v1/me/workspace")
    workspace = await client.get("/api/v1/me/workspace", headers=verified())
    merge = await client.post(
        "/api/v1/me/workspace/merge",
        headers=verified(),
        json={"shortlistListingIds": [], "comparisonListingIds": [], "savedSearches": [], "conversations": []},
    )

    assert missing.status_code == 401
    assert workspace.status_code == 200
    assert workspace.json()["shortlistListingIds"] == ["cv-toyota-rav4-2021-02"]
    assert merge.json()["ignoredListingIds"] == ["missing-listing"]
    assert repository.users == ["user_clerk_1", "user_clerk_1"]


@pytest.mark.anyio
async def test_shortlist_and_comparison_routes_map_unknown_listings_and_validation(
    buyer_api: tuple[httpx.AsyncClient, FakeBuyerRepository],
) -> None:
    client, _ = buyer_api

    added = await client.put("/api/v1/me/shortlist/cv-toyota-rav4-2021-02", headers=verified())
    removed = await client.delete("/api/v1/me/shortlist/cv-toyota-rav4-2021-02", headers=verified())
    missing = await client.put("/api/v1/me/shortlist/missing-listing", headers=verified())
    comparison = await client.put(
        "/api/v1/me/comparison", headers=verified(), json={"listingIds": ["one", "two"]}
    )
    duplicate = await client.put(
        "/api/v1/me/comparison", headers=verified(), json={"listingIds": ["one", "one"]}
    )

    assert added.status_code == removed.status_code == comparison.status_code == 200
    assert comparison.json()["comparisonListingIds"] == ["one", "two"]
    assert missing.status_code == 404
    assert missing.json()["type"].endswith("/listing-not-found")
    assert duplicate.status_code == 422


@pytest.mark.anyio
async def test_saved_search_routes_hide_foreign_ids_and_reject_empty_canonical_queries(
    buyer_api: tuple[httpx.AsyncClient, FakeBuyerRepository],
) -> None:
    client, _ = buyer_api

    listed = await client.get("/api/v1/me/saved-searches", headers=verified())
    saved = await client.post(
        "/api/v1/me/saved-searches", headers=verified(), json={"label": "RAV4", "query": "make=Toyota"}
    )
    invalid = await client.post(
        "/api/v1/me/saved-searches", headers=verified(), json={"label": "Invalid", "query": "?"}
    )
    deleted = await client.delete(f"/api/v1/me/saved-searches/{SAVED_ID}", headers=verified())
    foreign = await client.delete(
        "/api/v1/me/saved-searches/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", headers=verified()
    )

    assert listed.status_code == 200
    assert listed.json() == []
    assert saved.status_code == 200
    assert saved.json()["createdAt"] == "2026-08-22T12:00:00Z"
    assert invalid.status_code == 422
    assert invalid.json()["type"].endswith("/validation")
    assert deleted.status_code == 204
    assert foreign.status_code == 404


@pytest.mark.anyio
async def test_conversation_routes_preserve_ownership_and_ordered_turn_contract(
    buyer_api: tuple[httpx.AsyncClient, FakeBuyerRepository],
) -> None:
    client, _ = buyer_api

    listed = await client.get("/api/v1/me/conversations", headers=verified())
    created = await client.post(
        "/api/v1/me/conversations",
        headers=verified(),
        json={"clientId": "browser-1", "title": "Family SUV", "interpretedIntent": {}, "turns": []},
    )
    detail = await client.get(f"/api/v1/me/conversations/{CONVERSATION_ID}", headers=verified())
    appended = await client.post(
        f"/api/v1/me/conversations/{CONVERSATION_ID}/turns",
        headers=verified(),
        json={"role": "buyer", "content": "I need seven seats"},
    )
    foreign = await client.get(
        "/api/v1/me/conversations/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", headers=verified()
    )

    assert listed.status_code == created.status_code == detail.status_code == appended.status_code == 200
    assert listed.json()[0]["updatedAt"] == "2026-08-22T12:00:00Z"
    assert created.json()["clientId"] == "browser-1"
    assert appended.json()["turns"][0]["sequence"] == 0
    assert foreign.status_code == 404


@pytest.mark.anyio
async def test_public_routes_stay_public_and_cors_allows_authorization(
    buyer_api: tuple[httpx.AsyncClient, FakeBuyerRepository],
) -> None:
    client, _ = buyer_api

    health = await client.get("/health")
    preflight = await client.options(
        "/api/v1/me/workspace",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Authorization",
        },
    )

    assert health.status_code == 200
    assert preflight.status_code == 200
    assert "authorization" in preflight.headers["access-control-allow-headers"].lower()
