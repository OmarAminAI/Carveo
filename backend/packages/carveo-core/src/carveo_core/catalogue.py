from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from typing import Protocol

from carveo_core.contracts import (
    CompareRequest,
    CompareResponse,
    Listing,
    ListingPage,
    ListingQuery,
    ModelInsights,
    ModelMarketSummary,
)
from carveo_core.valuation import calculate_deal_position


class CatalogueRepository(Protocol):
    async def search(self, query: ListingQuery) -> ListingPage: ...

    async def get_by_id(self, listing_id: str) -> Listing | None: ...

    async def get_related(self, listing_id: str, limit: int = 4) -> list[Listing]: ...

    async def compare(self, request: CompareRequest) -> CompareResponse: ...

    async def get_model_insights(self, make: str, model: str) -> ModelInsights | None: ...


def with_deal_position(listing: Listing, catalogue: Sequence[Listing]) -> Listing:
    comparables = [
        candidate.price
        for candidate in catalogue
        if candidate.id != listing.id
        and candidate.market == listing.market
        and candidate.make.casefold() == listing.make.casefold()
        and candidate.model.casefold() == listing.model.casefold()
        and candidate.specifications == listing.specifications
        and abs(candidate.year - listing.year) <= 2
    ]
    return listing.model_copy(update={"deal_position": calculate_deal_position(listing.price, comparables)})


class FixtureCatalogueRepository:
    def __init__(self, listings: Sequence[Listing]) -> None:
        self._listings = list(listings)

    async def search(self, query: ListingQuery) -> ListingPage:
        items = self._filter(query)
        items = self._sort(items, query.sort)
        total = len(items)
        start = (query.page - 1) * query.page_size
        page_items = [with_deal_position(item, self._listings) for item in items[start : start + query.page_size]]
        return ListingPage(
            items=page_items,
            total=total,
            page=query.page,
            page_size=query.page_size,
            page_count=math.ceil(total / query.page_size) if total else 0,
        )

    async def get_by_id(self, listing_id: str) -> Listing | None:
        item = next((item for item in self._listings if item.id == listing_id), None)
        return with_deal_position(item, self._listings) if item else None

    async def get_related(self, listing_id: str, limit: int = 4) -> list[Listing]:
        item = next((candidate for candidate in self._listings if candidate.id == listing_id), None)
        if item is None:
            return []
        related = [
            candidate
            for candidate in self._listings
            if candidate.id != item.id and (candidate.model == item.model or candidate.body_type == item.body_type)
        ]
        return [with_deal_position(candidate, self._listings) for candidate in related[:limit]]

    async def compare(self, request: CompareRequest) -> CompareResponse:
        by_id = {item.id: item for item in self._listings}
        found = [
            with_deal_position(by_id[item_id], self._listings) for item_id in request.listing_ids if item_id in by_id
        ]
        missing = [item_id for item_id in request.listing_ids if item_id not in by_id]
        return CompareResponse(items=found, missing_ids=missing)

    async def get_model_insights(self, make: str, model: str) -> ModelInsights | None:
        items = [
            item
            for item in self._listings
            if item.make.casefold() == make.casefold() and item.model.casefold() == model.casefold()
        ]
        if not items:
            return None
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
        return ModelInsights(summary=summary, listings=[with_deal_position(item, self._listings) for item in items])

    def _filter(self, query: ListingQuery) -> list[Listing]:
        search = query.q.casefold()

        def matches(item: Listing) -> bool:
            haystack = f"{item.title} {item.make} {item.model} {item.trim} {item.description}".casefold()
            evidence = {claim.kind for claim in item.condition_evidence}
            requested_evidence = set(query.evidence)
            if "stated" in requested_evidence:
                requested_evidence.remove("stated")
                requested_evidence.update({"positive", "warning"})
            return (
                (not search or search in haystack)
                and (not query.make or item.make in query.make)
                and (not query.model or item.model in query.model)
                and (not query.body_type or item.body_type in query.body_type)
                and (query.year_min is None or item.year >= query.year_min)
                and (query.year_max is None or item.year <= query.year_max)
                and (query.price_min is None or item.price >= query.price_min)
                and (query.price_max is None or item.price <= query.price_max)
                and (query.mileage_max is None or item.mileage_km <= query.mileage_max)
                and (not query.specifications or item.specifications in query.specifications)
                and (not query.seller_type or item.seller_type in query.seller_type)
                and (not requested_evidence or bool(evidence.intersection(requested_evidence)))
                and (not query.city or item.city in query.city)
            )

        return [item for item in self._listings if matches(item)]

    def _sort(self, items: list[Listing], sort: str) -> list[Listing]:
        if sort == "lowest-price":
            return sorted(items, key=lambda item: item.price)
        if sort == "lowest-mileage":
            return sorted(items, key=lambda item: item.mileage_km)
        if sort == "newest":
            return sorted(items, key=lambda item: item.last_seen_at, reverse=True)
        if sort == "best-deal":

            def deal_score(item: Listing) -> float:
                position = with_deal_position(item, self._listings).deal_position
                if position is None or position.difference_percent is None:
                    return float("inf")
                return position.difference_percent

            return sorted(items, key=deal_score)
        return sorted(items, key=lambda item: item.last_seen_at, reverse=True)
