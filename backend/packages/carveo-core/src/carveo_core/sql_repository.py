from __future__ import annotations

import math
import statistics
from typing import Any

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.elements import ColumnElement

from carveo_core.catalogue import with_deal_position
from carveo_core.contracts import (
    CompareRequest,
    CompareResponse,
    Listing,
    ListingPage,
    ListingQuery,
    ModelInsights,
    ModelMarketSummary,
)
from carveo_core.models import ConditionEvidenceRecord, ListingRecord


def _options() -> tuple[ExecutableOption, ...]:
    return (
        selectinload(ListingRecord.source),
        selectinload(ListingRecord.photos),
        selectinload(ListingRecord.condition_evidence),
        selectinload(ListingRecord.price_observations),
        selectinload(ListingRecord.duplicate_offers),
    )


def record_to_contract(record: ListingRecord) -> Listing:
    return Listing.model_validate(
        {
            "id": record.public_id,
            "market": record.market,
            "title": record.title,
            "make": record.make,
            "model": record.model,
            "trim": record.trim,
            "year": record.year,
            "price": record.price,
            "currency": record.currency,
            "mileage_km": record.mileage_km,
            "city": record.city,
            "body_type": record.body_type,
            "specifications": record.specifications,
            "seller_type": record.seller_type,
            "source": {
                "name": record.source.name,
                "listing_url": record.source_url,
                "status": "Fixture" if record.source.authorization_status == "fixture" else "Approved",
            },
            "description": record.description,
            "features": record.features,
            "photos": [f"/api/v1/media/{photo.id}" if photo.storage_key else photo.url for photo in record.photos],
            "first_seen_at": record.first_seen_at,
            "last_seen_at": record.last_seen_at,
            "condition_evidence": [
                {
                    "kind": evidence.kind,
                    "label": evidence.label,
                    "detail": evidence.detail,
                    "source_claim": evidence.source_claim,
                }
                for evidence in record.condition_evidence
            ],
            "price_history": [
                {"observed_at": observation.observed_at, "price": observation.price}
                for observation in record.price_observations
                if observation.listing_id == record.id
            ],
            "duplicate_offers": [
                {"source": offer.source, "price": offer.price, "url": offer.url} for offer in record.duplicate_offers
            ],
        }
    )


class SqlAlchemyCatalogueRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _active_catalogue(self) -> list[Listing]:
        statement = select(ListingRecord).where(ListingRecord.lifecycle_status == "active").options(*_options())
        return [record_to_contract(record) for record in await self._session.scalars(statement)]

    def _filtered(self, query: ListingQuery) -> Select[tuple[ListingRecord]]:
        statement = select(ListingRecord).where(
            ListingRecord.market == query.market,
            ListingRecord.lifecycle_status == "active",
        )
        if query.q:
            terms = f"%{query.q}%"
            statement = statement.where(
                or_(
                    ListingRecord.searchable_text.match(query.q, postgresql_regconfig="simple"),
                    ListingRecord.searchable_text.ilike(terms),
                    func.similarity(ListingRecord.searchable_text, query.q) > 0.15,
                )
            )
        filters = (
            (query.make, ListingRecord.make),
            (query.model, ListingRecord.model),
            (query.body_type, ListingRecord.body_type),
            (query.specifications, ListingRecord.specifications),
            (query.seller_type, ListingRecord.seller_type),
            (query.city, ListingRecord.city),
        )
        for values, column in filters:
            if values:
                statement = statement.where(column.in_(values))
        if query.year_min is not None:
            statement = statement.where(ListingRecord.year >= query.year_min)
        if query.year_max is not None:
            statement = statement.where(ListingRecord.year <= query.year_max)
        if query.price_min is not None:
            statement = statement.where(ListingRecord.price >= query.price_min)
        if query.price_max is not None:
            statement = statement.where(ListingRecord.price <= query.price_max)
        if query.mileage_max is not None:
            statement = statement.where(ListingRecord.mileage_km <= query.mileage_max)
        if query.evidence:
            requested_evidence = set(query.evidence)
            if "stated" in requested_evidence:
                requested_evidence.remove("stated")
                requested_evidence.update({"positive", "warning"})
            statement = statement.where(
                ListingRecord.condition_evidence.any(ConditionEvidenceRecord.kind.in_(requested_evidence))
            )
        return statement

    async def search(self, query: ListingQuery) -> ListingPage:
        filtered = self._filtered(query)
        total = await self._session.scalar(select(func.count()).select_from(filtered.subquery())) or 0
        orders: dict[str, ColumnElement[Any]] = {
            "newest": ListingRecord.last_seen_at.desc(),
            "lowest-price": ListingRecord.price.asc(),
            "lowest-mileage": ListingRecord.mileage_km.asc(),
        }
        order = orders.get(query.sort, ListingRecord.last_seen_at.desc())
        catalogue = await self._active_catalogue()
        if query.sort == "best-deal":
            records = list(await self._session.scalars(filtered.options(*_options())))
            enriched = [with_deal_position(record_to_contract(record), catalogue) for record in records]
            enriched.sort(
                key=lambda item: item.deal_position.difference_percent
                if item.deal_position and item.deal_position.difference_percent is not None
                else float("inf")
            )
            start = (query.page - 1) * query.page_size
            return ListingPage(
                items=enriched[start : start + query.page_size],
                total=total,
                page=query.page,
                page_size=query.page_size,
                page_count=math.ceil(total / query.page_size) if total else 0,
            )
        statement = (
            filtered.order_by(order)
            .offset((query.page - 1) * query.page_size)
            .limit(query.page_size)
            .options(*_options())
        )
        records = list(await self._session.scalars(statement))
        items = [with_deal_position(record_to_contract(record), catalogue) for record in records]
        return ListingPage(
            items=items,
            total=total,
            page=query.page,
            page_size=query.page_size,
            page_count=math.ceil(total / query.page_size) if total else 0,
        )

    async def get_by_id(self, listing_id: str) -> Listing | None:
        statement = (
            select(ListingRecord)
            .where(ListingRecord.public_id == listing_id, ListingRecord.lifecycle_status == "active")
            .options(*_options())
        )
        record = await self._session.scalar(statement)
        if record is None:
            return None
        return with_deal_position(record_to_contract(record), await self._active_catalogue())

    async def get_related(self, listing_id: str, limit: int = 4) -> list[Listing]:
        source = await self._session.scalar(
            select(ListingRecord).where(
                ListingRecord.public_id == listing_id,
                ListingRecord.lifecycle_status == "active",
            )
        )
        if source is None:
            return []
        statement = (
            select(ListingRecord)
            .where(
                ListingRecord.public_id != listing_id,
                ListingRecord.lifecycle_status == "active",
                or_(ListingRecord.model == source.model, ListingRecord.body_type == source.body_type),
            )
            .order_by((ListingRecord.model == source.model).desc(), ListingRecord.last_seen_at.desc())
            .limit(limit)
            .options(*_options())
        )
        catalogue = await self._active_catalogue()
        return [
            with_deal_position(record_to_contract(record), catalogue)
            for record in await self._session.scalars(statement)
        ]

    async def compare(self, request: CompareRequest) -> CompareResponse:
        statement = (
            select(ListingRecord)
            .where(
                ListingRecord.public_id.in_(request.listing_ids),
                ListingRecord.lifecycle_status == "active",
            )
            .options(*_options())
        )
        records = {record.public_id: record for record in await self._session.scalars(statement)}
        catalogue = await self._active_catalogue()
        return CompareResponse(
            items=[
                with_deal_position(record_to_contract(records[item_id]), catalogue)
                for item_id in request.listing_ids
                if item_id in records
            ],
            missing_ids=[item_id for item_id in request.listing_ids if item_id not in records],
        )

    async def get_model_insights(self, make: str, model: str) -> ModelInsights | None:
        statement = (
            select(ListingRecord)
            .where(
                func.lower(ListingRecord.make) == make.lower(),
                func.lower(ListingRecord.model) == model.lower(),
                ListingRecord.lifecycle_status == "active",
            )
            .options(*_options())
        )
        records = list(await self._session.scalars(statement))
        if not records:
            return None
        items = [record_to_contract(record) for record in records]
        prices = [item.price for item in items]
        mileage = [item.mileage_km for item in items]
        summary = ModelMarketSummary(
            make=items[0].make,
            model=items[0].model,
            active_listings=len(items),
            median_price=round(statistics.median(prices)),
            min_price=min(prices),
            max_price=max(prices),
            min_mileage=min(mileage),
            max_mileage=max(mileage),
            last_updated_at=max(item.last_seen_at for item in items),
        )
        catalogue = await self._active_catalogue()
        return ModelInsights(summary=summary, listings=[with_deal_position(item, catalogue) for item in items])
