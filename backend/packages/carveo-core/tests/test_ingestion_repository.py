from __future__ import annotations

import asyncio
import os
import selectors
import subprocess
import warnings
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from carveo_core.contracts import CompareRequest
from carveo_core.database import create_engine, create_session_factory
from carveo_core.ingestion import CachedPhotoWrite, CreateRun
from carveo_core.ingestion_contracts import (
    ListingReference,
    NormalizedConditionEvidence,
    NormalizedListing,
    NormalizedPhoto,
    SourceQuery,
)
from carveo_core.ingestion_sql_repository import SqlAlchemyIngestionRepository
from carveo_core.models import (
    BuyerComparisonItemRecord,
    BuyerProfileRecord,
    BuyerShortlistItemRecord,
    CrawlRunRecord,
    ListingPhoto,
    ListingRecord,
    PriceObservationRecord,
    Source,
)
from carveo_core.sql_repository import SqlAlchemyCatalogueRepository
from docker.errors import DockerException
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

pytestmark = [pytest.mark.integration, pytest.mark.anyio]

NOW = datetime(2026, 9, 4, 10, 0, tzinfo=UTC)
SOURCE_ID = UUID("00000000-0000-0000-0000-000000000101")


@pytest.fixture(scope="module")
def anyio_backend() -> tuple[str, dict[str, object]]:
    return "asyncio", {"loop_factory": lambda: asyncio.SelectorEventLoop(selectors.SelectSelector())}


@pytest.fixture(scope="module")
def postgres_database_url() -> Iterator[str]:
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="The @wait_container_is_ready decorator is deprecated.*")
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
    yield create_session_factory(engine)
    await engine.dispose()


@pytest.fixture
async def repository(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[SqlAlchemyIngestionRepository]:
    async with session_factory() as session, session.begin():
        await session.execute(text("TRUNCATE TABLE sources CASCADE"))
        session.add(
            Source(
                id=SOURCE_ID,
                key="carveo-fixture",
                name="Carveo Fixture Source",
                market="ae",
                authorization_status="fixture",
                enabled=True,
                terms_reviewed_at=NOW,
                adapter_version="fixture-v1",
                parser_version="fixture-parser-v1",
                environment_allowlist=["development", "test"],
                allowed_hosts=["fixture-origin"],
                allowed_schemes=["http"],
                concurrency_limit=2,
                rate_limit_per_minute=30,
            )
        )
    yield SqlAlchemyIngestionRepository(session_factory)


def create_run(correlation_key: str, *, scenario: str = "baseline", at: datetime = NOW) -> CreateRun:
    return CreateRun(
        source_id=SOURCE_ID,
        query=SourceQuery(query_key="popular-uae", fixture_scenario=scenario),
        trigger="manual",
        correlation_key=correlation_key,
        adapter_version="fixture-v1",
        parser_version="fixture-parser-v1",
        queued_at=at,
    )


def listing(
    *,
    source_listing_id: str | None = "fixture-001",
    price: int = 118_000,
    mileage: int = 31_000,
    description: str = "Source description",
    source_sold: bool = False,
    at: datetime = NOW,
) -> NormalizedListing:
    reference = ListingReference(
        source_key="carveo-fixture",
        source_listing_id=source_listing_id,
        canonical_url=f"http://fixture-origin:8080/listings/{source_listing_id or 'missing'}.html",
        discovered_at=at,
        search_page_key="popular-uae:baseline:1",
    )
    return NormalizedListing(
        reference=reference,
        market="ae",
        title="Toyota RAV4 Adventure",
        make="Toyota",
        model="RAV4",
        trim="Adventure",
        year=2023,
        price=price,
        currency="AED",
        mileage_km=mileage,
        city="Dubai",
        body_type="SUV",
        specifications="GCC",
        seller_type="Dealer",
        description=description,
        features=["Sunroof"],
        photos=[
            NormalizedPhoto(
                source_url="http://fixture-origin:8080/media/fixture-suv.jpg",
                provenance="fixture",
                source_media_id="front",
            )
        ],
        condition_evidence=[
            NormalizedConditionEvidence(
                kind="unknown",
                label="Condition not stated",
                detail="The source did not provide condition evidence.",
            )
        ],
        source_sold=source_sold,
        original_values={"price": f"AED {price}"},
        extracted_at=at,
    )


async def observed_run(
    repository: SqlAlchemyIngestionRepository,
    *,
    correlation_key: str,
    item: NormalizedListing,
    at: datetime = NOW,
) -> tuple[UUID, str]:
    run = await repository.create_run(create_run(correlation_key, at=at))
    await repository.claim_run(run.id, started_at=at)
    await repository.record_item(
        run.id,
        item.reference,
        identity_key=f"{item.reference.source_key}:{item.reference.source_listing_id}",
    )
    outcome = await repository.upsert_listing(run.id, item)
    await repository.finalize_run(run.id, discovery_complete=True, finished_at=at)
    return run.id, outcome.public_id


async def test_create_run_is_idempotent_by_hourly_correlation_key(
    repository: SqlAlchemyIngestionRepository,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    first = await repository.create_run(create_run("fixture:popular-uae:2026-09-04T10"))
    second = await repository.create_run(create_run("fixture:popular-uae:2026-09-04T10"))

    assert first.id == second.id
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(CrawlRunRecord)) == 1


async def test_invalid_item_does_not_poison_a_later_valid_listing_transaction(
    repository: SqlAlchemyIngestionRepository,
) -> None:
    run = await repository.create_run(create_run("transaction-isolation"))
    await repository.claim_run(run.id, started_at=NOW)

    with pytest.raises(ValueError, match="source_listing_id"):
        await repository.upsert_listing(run.id, listing(source_listing_id=None))

    outcome = await repository.upsert_listing(run.id, listing())
    assert outcome.outcome == "created"


async def test_upsert_distinguishes_unchanged_price_and_non_price_changes(
    repository: SqlAlchemyIngestionRepository,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    run = await repository.create_run(create_run("upsert-outcomes"))
    await repository.claim_run(run.id, started_at=NOW)

    created = await repository.upsert_listing(run.id, listing())
    unchanged = await repository.upsert_listing(run.id, listing(at=NOW + timedelta(minutes=1)))
    text_changed = await repository.upsert_listing(
        run.id,
        listing(description="Updated source description", at=NOW + timedelta(minutes=2)),
    )
    price_changed = await repository.upsert_listing(
        run.id,
        listing(price=112_000, at=NOW + timedelta(minutes=3)),
    )

    assert created.outcome == "created" and created.price_observation_created is True
    assert unchanged.outcome == "unchanged" and unchanged.price_observation_created is False
    assert text_changed.outcome == "updated" and text_changed.price_observation_created is False
    assert price_changed.outcome == "updated" and price_changed.price_observation_created is True
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(PriceObservationRecord)) == 2


async def test_complete_misses_remove_on_third_run_and_restore_same_public_id(
    repository: SqlAlchemyIngestionRepository,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, public_id = await observed_run(repository, correlation_key="seen", item=listing())

    for miss in range(1, 4):
        at = NOW + timedelta(hours=miss)
        run = await repository.create_run(create_run(f"miss-{miss}", scenario=f"missing-{miss}", at=at))
        await repository.claim_run(run.id, started_at=at)
        await repository.finalize_run(run.id, discovery_complete=True, finished_at=at)
        async with session_factory() as session:
            record = await session.scalar(select(ListingRecord).where(ListingRecord.public_id == public_id))
            assert record is not None
            assert record.consecutive_successful_misses == miss
            assert record.lifecycle_status == ("removed" if miss == 3 else "missing")

    restored_run = await repository.create_run(create_run("restored", scenario="restored", at=NOW + timedelta(hours=4)))
    await repository.claim_run(restored_run.id, started_at=NOW + timedelta(hours=4))
    restored = await repository.upsert_listing(restored_run.id, listing(at=NOW + timedelta(hours=4)))

    assert restored.outcome == "restored"
    assert restored.public_id == public_id


async def test_incomplete_discovery_does_not_advance_absence_state(
    repository: SqlAlchemyIngestionRepository,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, public_id = await observed_run(repository, correlation_key="incomplete-seen", item=listing())
    run = await repository.create_run(
        create_run("incomplete-failure", scenario="failures", at=NOW + timedelta(hours=1))
    )
    await repository.claim_run(run.id, started_at=NOW + timedelta(hours=1))

    await repository.finalize_run(run.id, discovery_complete=False, finished_at=NOW + timedelta(hours=1))

    async with session_factory() as session:
        record = await session.scalar(select(ListingRecord).where(ListingRecord.public_id == public_id))
        assert record is not None
        assert record.lifecycle_status == "active"
        assert record.consecutive_successful_misses == 0


async def test_source_sold_listing_is_hidden_from_catalogue_immediately(
    repository: SqlAlchemyIngestionRepository,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, public_id = await observed_run(repository, correlation_key="source-sold-active", item=listing())
    sold_at = NOW + timedelta(hours=1)
    sold_listing = listing(source_sold=True, at=sold_at)
    sold_run = await repository.create_run(create_run("source-sold-update", at=sold_at))
    await repository.claim_run(sold_run.id, started_at=sold_at)
    await repository.record_item(
        sold_run.id,
        sold_listing.reference,
        identity_key="carveo-fixture:fixture-001",
    )
    outcome = await repository.upsert_listing(sold_run.id, sold_listing)

    assert outcome.outcome == "updated"
    async with session_factory() as session:
        catalogue = SqlAlchemyCatalogueRepository(session)
        assert await catalogue.get_by_id(public_id) is None
        comparison = await catalogue.compare(CompareRequest(listing_ids=[public_id]))
        assert comparison.items == []
        assert comparison.missing_ids == [public_id]


async def test_catalogue_emits_stable_carveo_url_for_cached_media(
    repository: SqlAlchemyIngestionRepository,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, public_id = await observed_run(repository, correlation_key="cached-media", item=listing())
    photo_id = uuid4()
    async with session_factory() as session, session.begin():
        record = await session.scalar(select(ListingRecord).where(ListingRecord.public_id == public_id))
        assert record is not None
        session.add(
            ListingPhoto(
                id=photo_id,
                listing_id=record.id,
                position=0,
                url="internal-placeholder",
                source_url="http://fixture-origin:8080/media/fixture-suv.jpg",
                provenance="fixture",
                storage_key="sha256/aa/image.jpg",
            )
        )

    async with session_factory() as session:
        public_listing = await SqlAlchemyCatalogueRepository(session).get_by_id(public_id)

    assert public_listing is not None
    assert public_listing.photos == [f"/api/v1/media/{photo_id}"]


async def test_photo_swap_keeps_shared_object_until_the_last_reference_is_replaced(
    repository: SqlAlchemyIngestionRepository,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, first_public_id = await observed_run(repository, correlation_key="shared-photo-first", item=listing())
    _, second_public_id = await observed_run(
        repository,
        correlation_key="shared-photo-second",
        item=listing(source_listing_id="fixture-002"),
    )
    async with session_factory() as session:
        listing_ids = {
            record.public_id: record.id
            for record in await session.scalars(
                select(ListingRecord).where(ListingRecord.public_id.in_([first_public_id, second_public_id]))
            )
        }

    shared = cached_photo("a", "sha256/aa/shared.jpg")
    replacement = cached_photo("b", "sha256/bb/replacement.jpg")
    await repository.replace_listing_photos(listing_ids[first_public_id], [shared], NOW)
    await repository.replace_listing_photos(listing_ids[second_public_id], [shared], NOW)

    first_swap = await repository.replace_listing_photos(
        listing_ids[first_public_id],
        [replacement],
        NOW + timedelta(minutes=1),
    )
    second_swap = await repository.replace_listing_photos(
        listing_ids[second_public_id],
        [replacement],
        NOW + timedelta(minutes=1),
    )

    assert first_swap.obsolete_storage_keys == []
    assert second_swap.obsolete_storage_keys == ["sha256/aa/shared.jpg"]


async def test_concurrent_finalization_reconciles_absence_once(
    repository: SqlAlchemyIngestionRepository,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, public_id = await observed_run(repository, correlation_key="concurrent-seen", item=listing())
    run = await repository.create_run(create_run("concurrent-miss", scenario="missing-1", at=NOW + timedelta(hours=1)))
    await repository.claim_run(run.id, started_at=NOW + timedelta(hours=1))
    second_repository = SqlAlchemyIngestionRepository(session_factory)

    await asyncio.gather(
        repository.finalize_run(run.id, discovery_complete=True, finished_at=NOW + timedelta(hours=1)),
        second_repository.finalize_run(run.id, discovery_complete=True, finished_at=NOW + timedelta(hours=1)),
    )

    async with session_factory() as session:
        record = await session.scalar(select(ListingRecord).where(ListingRecord.public_id == public_id))
        assert record is not None
        assert record.consecutive_successful_misses == 1


def cached_photo(hash_character: str, storage_key: str) -> CachedPhotoWrite:
    return CachedPhotoWrite(
        position=0,
        source_url="http://fixture-origin:8080/media/fixture-suv.jpg",
        provenance="fixture",
        source_media_id="front",
        storage_key=storage_key,
        content_hash=hash_character * 64,
        media_type="image/jpeg",
        byte_size=100,
    )


async def test_purge_deletes_listing_media_and_buyer_references_but_anonymizes_prices(
    repository: SqlAlchemyIngestionRepository,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    _, public_id = await observed_run(repository, correlation_key="purge-seen", item=listing())
    async with session_factory() as session, session.begin():
        record = await session.scalar(select(ListingRecord).where(ListingRecord.public_id == public_id))
        assert record is not None
        record.lifecycle_status = "removed"
        record.removed_at = NOW - timedelta(days=8)
        record.purge_at = NOW - timedelta(days=1)
        session.add(
            ListingPhoto(
                listing_id=record.id,
                position=0,
                url="/api/v1/media/test-photo",
                source_url="http://fixture-origin:8080/media/fixture-suv.jpg",
                provenance="fixture",
                storage_key="sha256/aa/image.jpg",
            )
        )
        buyer = BuyerProfileRecord(id=uuid4(), clerk_user_id="purge-user")
        session.add(buyer)
        await session.flush()
        session.add_all(
            [
                BuyerShortlistItemRecord(buyer_profile_id=buyer.id, listing_id=record.id),
                BuyerComparisonItemRecord(buyer_profile_id=buyer.id, listing_id=record.id, position=0),
            ]
        )

    summary = await repository.purge_due(NOW)

    assert summary.deleted_listing_count == 1
    assert summary.storage_keys == ["sha256/aa/image.jpg"]
    async with session_factory() as session:
        assert await session.scalar(select(func.count()).select_from(ListingRecord)) == 0
        assert await session.scalar(select(func.count()).select_from(BuyerShortlistItemRecord)) == 0
        assert await session.scalar(select(func.count()).select_from(BuyerComparisonItemRecord)) == 0
        observation = await session.scalar(select(PriceObservationRecord))
        assert observation is not None and observation.listing_id is None
