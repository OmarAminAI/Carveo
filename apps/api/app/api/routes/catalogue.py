from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import SavedSearchRecord
from app.db.session import get_db
from app.schemas.catalog import (
    CatalogueListing,
    CompareRequest,
    CompareResponse,
    ListingFilters,
    ListingPage,
    MarketResponse,
    SavedSearchInput,
    SavedSearchResponse,
)
from app.services.catalogue import catalogue_filters, get_listing, search_catalogue

router = APIRouter(tags=["marketplace"])


@router.get("/markets", response_model=list[MarketResponse])
def get_markets() -> list[MarketResponse]:
    return [MarketResponse(code="AE", name="United Arab Emirates", currency="AED", launched=True, source_count=1)]


@router.get("/listings", response_model=ListingPage)
def get_listings(
    market: str = "AE", query: str | None = None, make: str | None = None, model: str | None = None,
    body_type: str | None = None, year_min: int | None = None, year_max: int | None = None,
    price_max: int | None = None, mileage_max_km: int | None = None, specs: str | None = None,
    seller_type: str | None = None, sort: str = "best_deal", page: int = Query(1, ge=1), page_size: int = Query(12, ge=1, le=24),
) -> ListingPage:
    filters = ListingFilters(market=market, query=query, make=make, model=model, body_type=body_type, year_min=year_min, year_max=year_max, price_max=price_max, mileage_max_km=mileage_max_km, specs=specs, seller_type=seller_type, sort=sort, page=page, page_size=page_size)
    items, total = search_catalogue(filters)
    return ListingPage(items=items, total=total, page=page, page_size=page_size, available_filters=catalogue_filters())


@router.get("/listings/{listing_id}", response_model=CatalogueListing)
def get_listing_detail(listing_id: str) -> CatalogueListing:
    listing = get_listing(listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return listing


@router.post("/compare", response_model=CompareResponse)
def compare_listings(request: CompareRequest) -> CompareResponse:
    listings = [get_listing(listing_id) for listing_id in request.listing_ids]
    if any(item is None for item in listings):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more listings were not found")
    return CompareResponse(listings=[item for item in listings if item])


@router.get("/profile/searches", response_model=list[SavedSearchResponse])
def get_saved_searches(profile_id: str, db: Session = Depends(get_db)) -> list[SavedSearchResponse]:
    records = db.scalars(select(SavedSearchRecord).where(SavedSearchRecord.profile_id == profile_id).order_by(SavedSearchRecord.created_at.desc())).all()
    return [SavedSearchResponse(id=item.id, profile_id=item.profile_id, name=item.name, query=item.query, priority_refresh=item.priority_refresh) for item in records]


@router.put("/profile/searches", response_model=SavedSearchResponse, status_code=status.HTTP_201_CREATED)
def save_search(request: SavedSearchInput, db: Session = Depends(get_db)) -> SavedSearchResponse:
    record = SavedSearchRecord(profile_id=request.profile_id, name=request.name, query=request.query, priority_refresh=request.priority_refresh)
    db.add(record); db.commit(); db.refresh(record)
    return SavedSearchResponse(id=record.id, profile_id=record.profile_id, name=record.name, query=record.query, priority_refresh=record.priority_refresh)


@router.delete("/profile/searches/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_search(search_id: str, profile_id: str, db: Session = Depends(get_db)) -> None:
    record = db.get(SavedSearchRecord, search_id)
    if not record or record.profile_id != profile_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved search not found")
    db.delete(record); db.commit()
