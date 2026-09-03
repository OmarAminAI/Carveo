from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from carveo_core.fixtures import load_fixture_listings
from carveo_core.models import (
    ConditionEvidenceRecord,
    DuplicateOfferRecord,
    ListingPhoto,
    ListingRecord,
    PriceObservationRecord,
    Source,
)


async def seed_fixtures(session: AsyncSession) -> int:
    source = await session.scalar(select(Source).where(Source.key == "carveo-fixture"))
    if source is None:
        source = Source(
            key="carveo-fixture",
            name="Carveo approved fixture",
            market="ae",
            authorization_status="fixture",
            enabled=True,
            terms_reviewed_at=datetime(2026, 9, 3, tzinfo=UTC),
            adapter_version="fixture-v1",
            parser_version="fixture-parser-v1",
            environment_allowlist=["development", "test"],
            allowed_hosts=["fixture-origin"],
            allowed_schemes=["http"],
            concurrency_limit=1,
            rate_limit_per_minute=30,
            rate_limit_metadata={},
        )
        session.add(source)
        await session.flush()

    existing = set((await session.scalars(select(ListingRecord.public_id))).all())
    created = 0
    for fixture in load_fixture_listings():
        if fixture.id in existing:
            continue
        record = ListingRecord(
            public_id=fixture.id,
            source_id=source.id,
            source_listing_id=fixture.id,
            source_url=fixture.source.listing_url,
            market=fixture.market,
            lifecycle_status="active",
            title=fixture.title,
            make=fixture.make,
            model=fixture.model,
            trim=fixture.trim,
            year=fixture.year,
            price=fixture.price,
            currency=fixture.currency,
            mileage_km=fixture.mileage_km,
            city=fixture.city,
            body_type=fixture.body_type,
            specifications=fixture.specifications,
            seller_type=fixture.seller_type,
            description=fixture.description,
            features=fixture.features,
            first_seen_at=fixture.first_seen_at,
            last_seen_at=fixture.last_seen_at,
            searchable_text=" ".join([fixture.title, fixture.make, fixture.model, fixture.trim, fixture.description]),
        )
        record.photos = [
            ListingPhoto(position=index, url=url, source_url=url, provenance="fixture")
            for index, url in enumerate(fixture.photos)
        ]
        record.condition_evidence = [
            ConditionEvidenceRecord(
                kind=evidence.kind,
                label=evidence.label,
                detail=evidence.detail,
                source_claim=evidence.source_claim,
                confidence=None,
            )
            for evidence in fixture.condition_evidence
        ]
        record.price_observations = [
            PriceObservationRecord(
                observed_at=observation.observed_at,
                price=observation.price,
                market=fixture.market,
                make=fixture.make,
                model=fixture.model,
                year=fixture.year,
                specifications=fixture.specifications,
                mileage_band_km=(fixture.mileage_km // 10_000) * 10_000,
                currency=fixture.currency,
            )
            for observation in fixture.price_history
        ]
        record.duplicate_offers = [
            DuplicateOfferRecord(source=offer.source, price=offer.price, url=offer.url)
            for offer in fixture.duplicate_offers
        ]
        session.add(record)
        created += 1
    await session.commit()
    return created
