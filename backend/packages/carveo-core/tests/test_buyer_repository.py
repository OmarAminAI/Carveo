from __future__ import annotations

import asyncio
import os
import selectors
import subprocess
import warnings
from collections.abc import AsyncIterator, Iterator
from datetime import UTC
from typing import Any

import pytest
from carveo_core.buyer import InvalidSavedSearchQueryError, UnknownListingError
from carveo_core.buyer_contracts import (
    AnonymousWorkspaceMergeRequest,
    ConversationCreate,
    ConversationTurnCreate,
    SavedSearchUpsert,
)
from carveo_core.buyer_sql_repository import SqlAlchemyBuyerWorkspaceRepository
from carveo_core.database import create_engine, create_session_factory
from carveo_core.models import BuyerProfileRecord
from carveo_core.seed import seed_fixtures
from docker.errors import DockerException
from sqlalchemy import delete, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

pytestmark = [
    pytest.mark.integration,
    pytest.mark.anyio,
]

LISTING_A = "cv-toyota-land-cruiser-2022-01"
LISTING_B = "cv-toyota-land-cruiser-2021-02"
LISTING_C = "cv-toyota-rav4-2022-01"
LISTING_D = "cv-nissan-patrol-2022-01"


class _AsyncRendezvous:
    def __init__(self, parties: int) -> None:
        self._barrier = asyncio.Barrier(parties)
        self.arrivals = 0

    async def wait(self) -> None:
        self.arrivals += 1
        await self._barrier.wait()


@pytest.fixture(scope="module")
def anyio_backend() -> tuple[str, dict[str, object]]:
    return "asyncio", {"loop_factory": lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())}


@pytest.fixture(scope="module")
def postgres_database_url() -> Iterator[str]:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="The @wait_container_is_ready decorator is deprecated.*",
            category=DeprecationWarning,
        )
        from testcontainers.postgres import PostgresContainer

    try:
        with PostgresContainer("postgres:18-alpine") as postgres:
            sync_url = postgres.get_connection_url().replace("psycopg2", "psycopg")
            subprocess.run(
                ["uv", "run", "alembic", "-c", "apps/api/alembic.ini", "upgrade", "head"],
                check=True,
                env={**os.environ, "CARVEO_DATABASE_URL": sync_url},
            )
            yield sync_url.replace("postgresql+psycopg", "postgresql+psycopg_async")
    except DockerException:
        pytest.skip("Docker is required for PostgreSQL repository tests")


@pytest.fixture(scope="module")
async def session_factory(
    postgres_database_url: str,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    engine = create_engine(postgres_database_url)
    factory = create_session_factory(engine)
    async with factory() as session:
        await seed_fixtures(session)
    yield factory
    await engine.dispose()


@pytest.fixture
async def repository(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[SqlAlchemyBuyerWorkspaceRepository]:
    await _clear_buyers(session_factory)
    async with session_factory() as session:
        yield SqlAlchemyBuyerWorkspaceRepository(session)
    await _clear_buyers(session_factory)


async def test_get_workspace_creates_one_profile_just_in_time(
    repository: SqlAlchemyBuyerWorkspaceRepository,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    first = await repository.get_workspace("user-jit")
    second = await repository.get_workspace("user-jit")

    assert first == second
    assert first.shortlist_listing_ids == []
    assert first.comparison_listing_ids == []
    assert first.saved_searches == []
    assert first.conversations == []
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(BuyerProfileRecord)) == 1


async def test_persisted_timestamps_are_normalized_to_utc_in_non_utc_session(
    repository: SqlAlchemyBuyerWorkspaceRepository,
) -> None:
    await repository._session.execute(text("SET TIME ZONE 'Asia/Dubai'"))
    await repository._session.commit()
    assert await repository._session.scalar(text("SHOW TIME ZONE")) == "Asia/Dubai"
    await repository._session.rollback()

    saved_search = await repository.upsert_saved_search(
        "user-timezone",
        SavedSearchUpsert(label="Dubai SUVs", query="bodyType=SUV"),
    )
    conversation = await repository.create_conversation(
        "user-timezone",
        ConversationCreate(
            client_id="timezone-client",
            title="Timezone conversation",
            turns=[ConversationTurnCreate(role="buyer", content="Find an SUV")],
        ),
    )
    merge = await repository.merge_anonymous("user-timezone", AnonymousWorkspaceMergeRequest())
    loaded_conversation = await repository.get_conversation("user-timezone", conversation.id)

    assert loaded_conversation is not None
    timestamps = [
        saved_search.created_at,
        saved_search.updated_at,
        conversation.created_at,
        conversation.updated_at,
        conversation.turns[0].created_at,
        loaded_conversation.created_at,
        loaded_conversation.updated_at,
        loaded_conversation.turns[0].created_at,
        merge.workspace.saved_searches[0].created_at,
        merge.workspace.saved_searches[0].updated_at,
        merge.workspace.conversations[0].updated_at,
        merge.workspace.anonymous_merged_at,
    ]
    assert all(timestamp is not None and timestamp.tzinfo is UTC for timestamp in timestamps)


async def test_shortlist_is_idempotent_isolated_and_rejects_unknown_listings(
    repository: SqlAlchemyBuyerWorkspaceRepository,
) -> None:
    await repository.add_shortlist("user-one", LISTING_A)
    repeated = await repository.add_shortlist("user-one", LISTING_A)

    assert repeated.shortlist_listing_ids == [LISTING_A]
    assert (await repository.get_workspace("user-two")).shortlist_listing_ids == []
    assert (await repository.remove_shortlist("user-two", LISTING_A)).shortlist_listing_ids == []
    assert (await repository.get_workspace("user-one")).shortlist_listing_ids == [LISTING_A]
    assert (await repository.remove_shortlist("user-one", LISTING_A)).shortlist_listing_ids == []
    assert (await repository.remove_shortlist("user-one", LISTING_A)).shortlist_listing_ids == []

    with pytest.raises(UnknownListingError) as error:
        await repository.add_shortlist("user-one", "missing-listing")
    assert error.value.listing_public_ids == ("missing-listing",)


async def test_comparison_replacement_preserves_order_and_is_atomic(
    repository: SqlAlchemyBuyerWorkspaceRepository,
) -> None:
    initial = await repository.replace_comparison("user-comparison", [LISTING_A, LISTING_B])
    assert initial.comparison_listing_ids == [LISTING_A, LISTING_B]

    with pytest.raises(UnknownListingError) as error:
        await repository.replace_comparison("user-comparison", [LISTING_C, "missing-listing"])
    assert error.value.listing_public_ids == ("missing-listing",)
    assert (await repository.get_workspace("user-comparison")).comparison_listing_ids == [LISTING_A, LISTING_B]

    replaced = await repository.replace_comparison("user-comparison", [LISTING_C, LISTING_A])
    assert replaced.comparison_listing_ids == [LISTING_C, LISTING_A]
    assert (await repository.replace_comparison("user-comparison", [])).comparison_listing_ids == []


async def test_saved_searches_canonicalize_deduplicate_and_cap_at_twelve(
    repository: SqlAlchemyBuyerWorkspaceRepository,
) -> None:
    first = await repository.upsert_saved_search(
        "user-searches",
        SavedSearchUpsert(label="SUVs", query="priceMax=200000&bodyType=SUV"),
    )
    updated = await repository.upsert_saved_search(
        "user-searches",
        SavedSearchUpsert(label="Family SUVs", query="bodyType=SUV&priceMax=200000"),
    )

    assert updated.id == first.id
    assert updated.label == "Family SUVs"
    assert updated.query == "bodyType=SUV&priceMax=200000"

    for index in range(1, 12):
        await repository.upsert_saved_search(
            "user-searches",
            SavedSearchUpsert(label=f"Search {index}", query=f"make=Toyota&page={index}"),
        )

    refreshed = await repository.upsert_saved_search(
        "user-searches",
        SavedSearchUpsert(label="SUVs refreshed", query="priceMax=200000&bodyType=SUV"),
    )
    before_thirteenth = await repository.get_workspace("user-searches")
    assert len(before_thirteenth.saved_searches) == 12
    assert before_thirteenth.saved_searches[0].id == refreshed.id

    await repository.upsert_saved_search(
        "user-searches",
        SavedSearchUpsert(label="Thirteenth", query="make=Nissan&page=13"),
    )
    after_thirteenth = await repository.get_workspace("user-searches")

    assert len(after_thirteenth.saved_searches) == 12
    assert "make=Toyota&page=1" not in {search.query for search in after_thirteenth.saved_searches}
    assert await repository.delete_saved_search("user-other", refreshed.id) is False
    assert await repository.delete_saved_search("user-searches", refreshed.id) is True
    assert await repository.delete_saved_search("user-searches", refreshed.id) is False


async def test_empty_canonical_saved_search_query_raises_domain_error_without_persisting(
    repository: SqlAlchemyBuyerWorkspaceRepository,
) -> None:
    with pytest.raises(InvalidSavedSearchQueryError, match="canonical query must not be empty"):
        await repository.upsert_saved_search(
            "user-invalid-search",
            SavedSearchUpsert(label="Invalid", query="?"),
        )

    workspace = await repository.get_workspace("user-invalid-search")
    assert workspace.saved_searches == []


async def test_conversations_hide_ownership_and_keep_turn_sequence(
    repository: SqlAlchemyBuyerWorkspaceRepository,
) -> None:
    created = await repository.create_conversation(
        "user-conversation",
        ConversationCreate(
            client_id="client-one",
            title="Family SUV",
            interpreted_intent={"bodyType": "SUV"},
            turns=[
                ConversationTurnCreate(role="buyer", content="Find an SUV"),
                ConversationTurnCreate(role="assistant", content="What budget?"),
            ],
        ),
    )
    repeated = await repository.create_conversation(
        "user-conversation",
        ConversationCreate(client_id="client-one", title="Replacement title"),
    )

    assert repeated.id == created.id
    assert repeated.title == "Family SUV"
    assert [turn.sequence for turn in repeated.turns] == [0, 1]
    assert await repository.get_conversation("user-other", created.id) is None
    assert (
        await repository.append_turn(
            "user-other",
            created.id,
            ConversationTurnCreate(role="buyer", content="Foreign append"),
        )
        is None
    )

    appended = await repository.append_turn(
        "user-conversation",
        created.id,
        ConversationTurnCreate(role="buyer", content="Up to AED 180k"),
    )

    assert appended is not None
    assert [turn.sequence for turn in appended.turns] == [0, 1, 2]
    assert [turn.content for turn in appended.turns] == ["Find an SUV", "What budget?", "Up to AED 180k"]


async def test_concurrent_turns_receive_distinct_monotonic_sequences(
    repository: SqlAlchemyBuyerWorkspaceRepository,
    session_factory: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    conversation = await repository.create_conversation(
        "user-turn-lock",
        ConversationCreate(client_id="turn-lock", title="Turn lock"),
    )

    rendezvous = _AsyncRendezvous(2)
    async with session_factory() as first_session, session_factory() as second_session:
        sessions = [first_session, second_session]
        repositories = [SqlAlchemyBuyerWorkspaceRepository(session) for session in sessions]
        for session in sessions:
            original_scalar = session.scalar

            async def synchronized_scalar(
                statement: object,
                *args: object,
                _original_scalar: Any = original_scalar,
                **kwargs: object,
            ) -> object:
                if getattr(statement, "_for_update_arg", None) is not None:
                    await rendezvous.wait()
                return await _original_scalar(statement, *args, **kwargs)

            monkeypatch.setattr(session, "scalar", synchronized_scalar)

        async def append(concurrent_repository: SqlAlchemyBuyerWorkspaceRepository, content: str) -> None:
            result = await concurrent_repository.append_turn(
                "user-turn-lock",
                conversation.id,
                ConversationTurnCreate(role="buyer", content=content),
            )
            assert result is not None

        await asyncio.wait_for(
            asyncio.gather(
                append(repositories[0], "First concurrent turn"),
                append(repositories[1], "Second concurrent turn"),
            ),
            timeout=5,
        )

    loaded = await repository.get_conversation("user-turn-lock", conversation.id)
    assert loaded is not None
    assert rendezvous.arrivals == 2
    assert [turn.sequence for turn in loaded.turns] == [0, 1]
    assert {turn.content for turn in loaded.turns} == {"First concurrent turn", "Second concurrent turn"}


async def test_merge_applies_server_first_rules_once_and_reports_unknown_ids_in_order(
    repository: SqlAlchemyBuyerWorkspaceRepository,
) -> None:
    await repository.add_shortlist("user-merge", LISTING_A)
    await repository.replace_comparison("user-merge", [LISTING_A, LISTING_B])
    server_search = await repository.upsert_saved_search(
        "user-merge",
        SavedSearchUpsert(label="Server label", query="bodyType=SUV&priceMax=200000"),
    )
    server_conversation = await repository.create_conversation(
        "user-merge",
        ConversationCreate(client_id="server-client", title="Server title"),
    )

    result = await repository.merge_anonymous(
        "user-merge",
        AnonymousWorkspaceMergeRequest(
            shortlist_listing_ids=[LISTING_B, "missing-shortlist"],
            comparison_listing_ids=[LISTING_B, LISTING_C, "missing-comparison", LISTING_D],
            saved_searches=[
                SavedSearchUpsert(label="Anonymous label", query="priceMax=200000&bodyType=SUV"),
                SavedSearchUpsert(label="Anonymous new", query="make=Nissan"),
            ],
            conversations=[
                ConversationCreate(client_id="server-client", title="Anonymous title"),
                ConversationCreate(
                    client_id="anonymous-client",
                    title="Anonymous conversation",
                    turns=[ConversationTurnCreate(role="buyer", content="Find a Patrol")],
                ),
            ],
        ),
    )

    assert result.merged is True
    assert result.ignored_listing_ids == ["missing-shortlist", "missing-comparison"]
    assert result.workspace.shortlist_listing_ids == [LISTING_A, LISTING_B]
    assert result.workspace.comparison_listing_ids == [LISTING_A, LISTING_B, LISTING_C, LISTING_D]
    assert result.workspace.anonymous_merged_at is not None
    assert {search.query: search.label for search in result.workspace.saved_searches} == {
        "bodyType=SUV&priceMax=200000": "Server label",
        "make=Nissan": "Anonymous new",
    }
    assert next(search.id for search in result.workspace.saved_searches if search.query.startswith("bodyType")) == (
        server_search.id
    )
    assert {conversation.title for conversation in result.workspace.conversations} == {
        "Server title",
        "Anonymous conversation",
    }
    assert (
        await repository.get_conversation("user-merge", server_conversation.id)
    ).title == "Server title"  # type: ignore[union-attr]

    repeated = await repository.merge_anonymous(
        "user-merge",
        AnonymousWorkspaceMergeRequest(shortlist_listing_ids=[LISTING_C, "another-missing"]),
    )
    assert repeated.merged is False
    assert repeated.ignored_listing_ids == []
    assert repeated.workspace.shortlist_listing_ids == [LISTING_A, LISTING_B]


async def test_concurrent_merge_stamps_exactly_once(
    repository: SqlAlchemyBuyerWorkspaceRepository,
    session_factory: async_sessionmaker[AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await repository.get_workspace("user-concurrent-merge")

    rendezvous = _AsyncRendezvous(2)
    async with session_factory() as first_session, session_factory() as second_session:
        repositories = [
            SqlAlchemyBuyerWorkspaceRepository(first_session),
            SqlAlchemyBuyerWorkspaceRepository(second_session),
        ]
        for concurrent_repository in repositories:
            original_get_or_create = concurrent_repository._get_or_create_profile

            async def synchronized_get_or_create(
                clerk_user_id: str,
                _original_get_or_create: Any = original_get_or_create,
            ) -> BuyerProfileRecord:
                profile = await _original_get_or_create(clerk_user_id)
                await rendezvous.wait()
                return profile

            monkeypatch.setattr(concurrent_repository, "_get_or_create_profile", synchronized_get_or_create)

        async def merge(
            concurrent_repository: SqlAlchemyBuyerWorkspaceRepository,
            listing_id: str,
        ) -> tuple[bool, list[str]]:
            response = await concurrent_repository.merge_anonymous(
                "user-concurrent-merge",
                AnonymousWorkspaceMergeRequest(shortlist_listing_ids=[listing_id]),
            )
            return response.merged, response.workspace.shortlist_listing_ids

        results = await asyncio.wait_for(
            asyncio.gather(merge(repositories[0], LISTING_A), merge(repositories[1], LISTING_B)),
            timeout=5,
        )

    assert rendezvous.arrivals == 2
    assert sorted(merged for merged, _ in results) == [False, True]
    winning_listing = next(shortlist[0] for merged, shortlist in results if merged)
    async with session_factory() as session:
        workspace = await SqlAlchemyBuyerWorkspaceRepository(session).get_workspace("user-concurrent-merge")
    assert workspace.shortlist_listing_ids == [winning_listing]


async def _clear_buyers(factory: async_sessionmaker[AsyncSession]) -> None:
    async with factory() as session, session.begin():
        await session.execute(delete(BuyerProfileRecord))
