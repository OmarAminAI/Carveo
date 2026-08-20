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
            ListingPhoto(position=index, url=url, provenance="fixture") for index, url in enumerate(fixture.photos)
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
            PriceObservationRecord(observed_at=observation.observed_at, price=observation.price)
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
