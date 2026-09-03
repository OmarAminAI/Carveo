from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Literal, cast
from uuid import UUID

from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from carveo_core.ingestion import CreateRun, LifecycleSummary, ListingWriteOutcome, PurgeSummary
from carveo_core.ingestion_contracts import CrawlRunSummary, ListingReference, NormalizedListing, RunStatus
from carveo_core.models import (
    BuyerComparisonItemRecord,
    BuyerShortlistItemRecord,
    ConditionEvidenceRecord,
    CrawlRunItemRecord,
    CrawlRunRecord,
    DuplicateOfferRecord,
    ExtractionArtifactRecord,
    ListingPhoto,
    ListingRecord,
    PriceObservationRecord,
    Source,
)

TERMINAL_STATUSES = {RunStatus.COMPLETED.value, RunStatus.PARTIAL.value, RunStatus.FAILED.value}
LISTING_RETENTION = timedelta(days=7)
ARTIFACT_RETENTION = timedelta(days=7)
RUN_RETENTION = timedelta(days=90)


class UnknownIngestionRunError(LookupError):
    pass


class SqlAlchemyIngestionRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def create_run(self, command: CreateRun) -> CrawlRunSummary:
        async with self._session_factory() as session:
            existing = await session.scalar(
                select(CrawlRunRecord).where(CrawlRunRecord.correlation_key == command.correlation_key)
            )
            if existing is not None:
                return await _run_summary(session, existing)
            record = CrawlRunRecord(
                source_id=command.source_id,
                query_key=command.query.query_key,
                fixture_scenario=command.query.fixture_scenario,
                trigger=command.trigger,
                correlation_key=command.correlation_key,
                adapter_version=command.adapter_version,
                parser_version=command.parser_version,
                status=RunStatus.QUEUED.value,
                discovery_complete=False,
                counters={},
                queued_at=command.queued_at,
                purge_at=command.queued_at + RUN_RETENTION,
            )
            session.add(record)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                winner = await session.scalar(
                    select(CrawlRunRecord).where(CrawlRunRecord.correlation_key == command.correlation_key)
                )
                if winner is None:
                    raise
                return await _run_summary(session, winner)
            await session.refresh(record)
            return await _run_summary(session, record)

    async def claim_run(self, run_id: UUID, *, started_at: datetime) -> CrawlRunSummary:
        async with self._session_factory() as session, session.begin():
            record = await _locked_run(session, run_id)
            if record.status == RunStatus.QUEUED.value:
                record.status = RunStatus.RUNNING.value
                record.started_at = _as_datetime(started_at)
            return await _run_summary(session, record)

    async def record_item(self, run_id: UUID, reference: ListingReference, *, identity_key: str) -> UUID:
        async with self._session_factory() as session:
            existing = await session.scalar(
                select(CrawlRunItemRecord).where(
                    CrawlRunItemRecord.run_id == run_id,
                    CrawlRunItemRecord.identity_key == identity_key,
                )
            )
            if existing is not None:
                return existing.id
            item = CrawlRunItemRecord(
                run_id=run_id,
                identity_key=identity_key,
                source_listing_id=reference.source_listing_id,
                canonical_url=reference.canonical_url,
                search_page_key=reference.search_page_key,
                discovered_at=reference.discovered_at,
                fetch_status="pending",
                parse_status="pending",
                attempt_count=0,
            )
            session.add(item)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                winner = await session.scalar(
                    select(CrawlRunItemRecord).where(
                        CrawlRunItemRecord.run_id == run_id,
                        CrawlRunItemRecord.identity_key == identity_key,
                    )
                )
                if winner is None:
                    raise
                return winner.id
            return item.id

    async def upsert_listing(self, run_id: UUID, listing: NormalizedListing) -> ListingWriteOutcome:
        source_listing_id = listing.reference.source_listing_id
        if source_listing_id is None:
            raise ValueError("source_listing_id is required for persistence")
        async with self._session_factory() as session, session.begin():
            run = await _locked_run(session, run_id)
            record = await session.scalar(
                select(ListingRecord)
                .where(
                    ListingRecord.source_id == run.source_id,
                    ListingRecord.source_listing_id == source_listing_id,
                )
                .with_for_update()
            )
            created = record is None
            restored = record is not None and record.lifecycle_status != "active"
            price_changed = record is None or record.price != listing.price or record.currency != listing.currency
            sold_state_changed = record is not None and (record.source_sold_at is not None) != listing.source_sold
            changed = record is None or sold_state_changed or _listing_values(record) != _normalized_values(listing)

            if record is None:
                record = ListingRecord(
                    id=uuid.uuid4(),
                    public_id=f"cv-{uuid.uuid4().hex[:20]}",
                    source_id=run.source_id,
                    source_listing_id=source_listing_id,
                    first_seen_at=listing.extracted_at,
                    last_seen_at=listing.extracted_at,
                    searchable_text="",
                    **_normalized_values(listing),
                )
                session.add(record)
            else:
                for field, value in _normalized_values(listing).items():
                    setattr(record, field, value)
                record.last_seen_at = listing.extracted_at

            if listing.source_sold:
                record.lifecycle_status = "removed"
                record.source_sold_at = listing.extracted_at
                record.removed_at = listing.extracted_at
                record.purge_at = listing.extracted_at + LISTING_RETENTION
            else:
                record.lifecycle_status = "active"
                record.missing_at = None
                record.removed_at = None
                record.source_sold_at = None
                record.purge_at = None
                record.consecutive_successful_misses = 0
                if restored:
                    record.restored_at = listing.extracted_at
            record.searchable_text = _searchable_text(listing)
            await session.flush()

            if changed:
                await session.execute(
                    delete(ConditionEvidenceRecord).where(ConditionEvidenceRecord.listing_id == record.id)
                )
                session.add_all(
                    [
                    ConditionEvidenceRecord(
                        listing_id=record.id,
                        kind=evidence.kind,
                        label=evidence.label,
                        detail=evidence.detail,
                        source_claim=evidence.source_claim,
                        confidence=evidence.confidence,
                    )
                    for evidence in listing.condition_evidence
                    ]
                )
            if price_changed:
                session.add(
                    PriceObservationRecord(
                        listing_id=record.id,
                        observed_at=listing.extracted_at,
                        price=listing.price,
                        market=listing.market,
                        make=listing.make,
                        model=listing.model,
                        year=listing.year,
                        specifications=listing.specifications,
                        mileage_band_km=(listing.mileage_km // 10_000) * 10_000,
                        currency=listing.currency,
                    )
                )

            identity_key = f"{listing.reference.source_key}:{source_listing_id}"
            item = await session.scalar(
                select(CrawlRunItemRecord).where(
                    CrawlRunItemRecord.run_id == run_id,
                    CrawlRunItemRecord.identity_key == identity_key,
                )
            )
            if item is not None:
                fingerprint, payload = _fingerprint(listing)
                item.listing_id = record.id
                item.fetch_status = "completed"
                item.parse_status = "completed"
                item.content_fingerprint = fingerprint
                item.completed_at = listing.extracted_at
                session.add(
                    ExtractionArtifactRecord(
                        run_item_id=item.id,
                        listing_id=record.id,
                        extraction_payload=payload,
                        extraction_evidence={"originalValues": listing.original_values},
                        parser_version=run.parser_version,
                        content_fingerprint=fingerprint,
                        purge_at=listing.extracted_at + ARTIFACT_RETENTION,
                    )
                )

            outcome: Literal["created", "updated", "unchanged", "restored"] = (
                "created" if created else "restored" if restored else "updated" if changed else "unchanged"
            )
            run.counters = _increment(run.counters, outcome)
            return ListingWriteOutcome(
                outcome=outcome,
                listing_id=record.id,
                public_id=record.public_id,
                price_observation_created=price_changed,
            )

    async def reconcile_absent(self, run_id: UUID, *, now: datetime) -> LifecycleSummary:
        async with self._session_factory() as session, session.begin():
            run = await _locked_run(session, run_id)
            return await self._reconcile_locked(session, run, _as_datetime(now))

    async def finalize_run(
        self,
        run_id: UUID,
        *,
        discovery_complete: bool,
        finished_at: datetime,
    ) -> CrawlRunSummary:
        async with self._session_factory() as session, session.begin():
            run = await _locked_run(session, run_id)
            if run.status in TERMINAL_STATUSES:
                return await _run_summary(session, run)
            finished = _as_datetime(finished_at)
            run.discovery_complete = discovery_complete
            if discovery_complete:
                lifecycle = await self._reconcile_locked(session, run, finished)
                run.counters = {
                    **run.counters,
                    "missing": lifecycle.missing_count,
                    "removed": lifecycle.removed_count,
                    "reconciled": 1,
                }
            failed_items = await session.scalar(
                select(func.count())
                .select_from(CrawlRunItemRecord)
                .where(
                    CrawlRunItemRecord.run_id == run_id,
                    (CrawlRunItemRecord.fetch_status == "failed")
                    | (CrawlRunItemRecord.parse_status.in_(["failed", "rejected"])),
                )
            )
            run.status = RunStatus.PARTIAL.value if failed_items else RunStatus.COMPLETED.value
            run.finished_at = finished
            return await _run_summary(session, run)

    async def mark_failed(self, run_id: UUID, *, error_code: str, finished_at: datetime) -> CrawlRunSummary:
        async with self._session_factory() as session, session.begin():
            run = await _locked_run(session, run_id)
            if run.status not in TERMINAL_STATUSES:
                run.status = RunStatus.FAILED.value
                run.error_code = error_code[:80]
                run.finished_at = _as_datetime(finished_at)
            return await _run_summary(session, run)

    async def purge_due(self, now: datetime) -> PurgeSummary:
        cutoff = _as_datetime(now)
        async with self._session_factory() as session, session.begin():
            listing_ids = list(
                await session.scalars(
                    select(ListingRecord.id).where(
                        ListingRecord.lifecycle_status == "removed",
                        ListingRecord.purge_at.is_not(None),
                        ListingRecord.purge_at <= cutoff,
                    )
                )
            )
            storage_keys: list[str] = []
            if listing_ids:
                storage_keys = list(
                    await session.scalars(
                        select(ListingPhoto.storage_key).where(
                            ListingPhoto.listing_id.in_(listing_ids),
                            ListingPhoto.storage_key.is_not(None),
                        )
                    )
                )
                run_item_ids = select(CrawlRunItemRecord.id).where(CrawlRunItemRecord.listing_id.in_(listing_ids))
                await session.execute(
                    delete(ExtractionArtifactRecord).where(ExtractionArtifactRecord.run_item_id.in_(run_item_ids))
                )
                await session.execute(delete(CrawlRunItemRecord).where(CrawlRunItemRecord.listing_id.in_(listing_ids)))
                await session.execute(
                    delete(BuyerShortlistItemRecord).where(BuyerShortlistItemRecord.listing_id.in_(listing_ids))
                )
                await session.execute(
                    delete(BuyerComparisonItemRecord).where(BuyerComparisonItemRecord.listing_id.in_(listing_ids))
                )
                await session.execute(
                    update(PriceObservationRecord)
                    .where(PriceObservationRecord.listing_id.in_(listing_ids))
                    .values(listing_id=None)
                )
                await session.execute(
                    delete(ConditionEvidenceRecord).where(ConditionEvidenceRecord.listing_id.in_(listing_ids))
                )
                await session.execute(delete(ListingPhoto).where(ListingPhoto.listing_id.in_(listing_ids)))
                await session.execute(
                    delete(DuplicateOfferRecord).where(DuplicateOfferRecord.listing_id.in_(listing_ids))
                )
                await session.execute(delete(ListingRecord).where(ListingRecord.id.in_(listing_ids)))

            artifact_result = await session.execute(
                delete(ExtractionArtifactRecord).where(ExtractionArtifactRecord.purge_at <= cutoff)
            )
            run_result = await session.execute(delete(CrawlRunRecord).where(CrawlRunRecord.purge_at <= cutoff))
            return PurgeSummary(
                deleted_listing_count=len(listing_ids),
                deleted_artifact_count=artifact_result.rowcount,  # type: ignore[attr-defined]
                deleted_run_count=run_result.rowcount,  # type: ignore[attr-defined]
                storage_keys=storage_keys,
            )

    async def _reconcile_locked(
        self,
        session: AsyncSession,
        run: CrawlRunRecord,
        now: datetime,
    ) -> LifecycleSummary:
        reconciled_at = _as_datetime(now)
        if not run.discovery_complete and run.counters.get("reconciled") != 1:
            return LifecycleSummary(missing_count=0, removed_count=0)
        if run.counters.get("reconciled") == 1:
            return LifecycleSummary(
                missing_count=run.counters.get("missing", 0),
                removed_count=run.counters.get("removed", 0),
            )
        seen_ids = select(CrawlRunItemRecord.listing_id).where(
            CrawlRunItemRecord.run_id == run.id,
            CrawlRunItemRecord.listing_id.is_not(None),
        )
        records = list(
            await session.scalars(
                select(ListingRecord)
                .where(
                    ListingRecord.source_id == run.source_id,
                    ListingRecord.lifecycle_status.in_(["active", "missing"]),
                    ListingRecord.source_sold_at.is_(None),
                    ListingRecord.id.not_in(seen_ids),
                )
                .with_for_update()
            )
        )
        missing_count = 0
        removed_count = 0
        for record in records:
            record.consecutive_successful_misses += 1
            if record.consecutive_successful_misses >= 3:
                record.lifecycle_status = "removed"
                record.removed_at = reconciled_at
                record.purge_at = reconciled_at + LISTING_RETENTION
                removed_count += 1
            else:
                record.lifecycle_status = "missing"
                record.missing_at = record.missing_at or reconciled_at
                missing_count += 1
        return LifecycleSummary(missing_count=missing_count, removed_count=removed_count)


async def _locked_run(session: AsyncSession, run_id: UUID) -> CrawlRunRecord:
    record = await session.scalar(select(CrawlRunRecord).where(CrawlRunRecord.id == run_id).with_for_update())
    if record is None:
        raise UnknownIngestionRunError(str(run_id))
    return record


async def _run_summary(session: AsyncSession, record: CrawlRunRecord) -> CrawlRunSummary:
    source_key = await session.scalar(select(Source.key).where(Source.id == record.source_id))
    if source_key is None:
        raise LookupError(f"Source for ingestion run {record.id} does not exist")
    return CrawlRunSummary(
        id=record.id,
        source_key=source_key,
        trigger=cast(Literal["manual", "scheduled"], record.trigger),
        status=RunStatus(record.status),
        discovery_complete=record.discovery_complete,
        counters=dict(record.counters),
        queued_at=record.queued_at,
        started_at=record.started_at,
        finished_at=record.finished_at,
        error_code=record.error_code,
    )


def _normalized_values(listing: NormalizedListing) -> dict[str, object]:
    return {
        "source_url": listing.reference.canonical_url,
        "market": listing.market,
        "title": listing.title,
        "make": listing.make,
        "model": listing.model,
        "trim": listing.trim,
        "year": listing.year,
        "price": listing.price,
        "currency": listing.currency,
        "mileage_km": listing.mileage_km,
        "city": listing.city,
        "body_type": listing.body_type,
        "specifications": listing.specifications,
        "seller_type": listing.seller_type,
        "description": listing.description,
        "features": list(listing.features),
    }


def _listing_values(record: ListingRecord) -> dict[str, object]:
    return {field: getattr(record, field) for field in _normalized_values_fields()}


def _normalized_values_fields() -> tuple[str, ...]:
    return (
        "source_url",
        "market",
        "title",
        "make",
        "model",
        "trim",
        "year",
        "price",
        "currency",
        "mileage_km",
        "city",
        "body_type",
        "specifications",
        "seller_type",
        "description",
        "features",
    )


def _searchable_text(listing: NormalizedListing) -> str:
    return " ".join(
        value
        for value in (listing.title, listing.make, listing.model, listing.trim, listing.city, listing.description)
        if value
    )


def _fingerprint(listing: NormalizedListing) -> tuple[str, dict[str, object]]:
    payload = listing.model_dump(mode="json")
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest(), payload


def _increment(counters: dict[str, int], key: str) -> dict[str, int]:
    return {**counters, key: counters.get(key, 0) + 1}


def _as_datetime(value: object) -> datetime:
    if not isinstance(value, datetime):
        raise TypeError("timestamp must be a datetime")
    return value
