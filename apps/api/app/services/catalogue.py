from datetime import UTC, datetime, timedelta
from statistics import median

from app.schemas.catalog import CatalogueListing, ConditionEvidence, ListingFilters


NOW = datetime.now(UTC)


def _listing(id: str, title: str, make: str, model: str, trim: str, body_type: str, price: int, year: int, mileage: int, city: str, seller: str, specs: str, color: str, hours: int, condition: list[ConditionEvidence], features: list[str]) -> CatalogueListing:
    return CatalogueListing(id=id, market="AE", source_id="dubizzle", source_name="Dubizzle", source_url="https://dubai.dubizzle.com/motors/used-cars/", title=title, make=make, model=model, trim=trim, body_type=body_type, price=price, year=year, mileage_km=mileage, city=city, seller_type=seller, regional_specs=specs, color=color, warranty="Warranty" in features, condition=condition, features=features, photos=[], first_seen_at=NOW - timedelta(days=max(1, hours // 24)), last_seen_at=NOW - timedelta(hours=hours), freshness_hours=hours)


CATALOGUE = [
    _listing("ae-001", "Mercedes-Benz C-Class C200 2023", "Mercedes-Benz", "C-Class", "C200", "Sedan", 172000, 2023, 38000, "Dubai", "Dealer", "GCC", "Black", 3, [ConditionEvidence(claim="Listing claims accident-free", evidence="Accident free", confidence=.78)], ["GCC specs", "Warranty", "Service history"]),
    _listing("ae-002", "Mercedes-Benz C-Class C300 2023", "Mercedes-Benz", "C-Class", "C300", "Sedan", 151000, 2023, 41000, "Abu Dhabi", "Private", "US", "Silver", 10, [ConditionEvidence(claim="Imported specs", evidence="US specs", confidence=.95), ConditionEvidence(claim="Condition not stated", confidence=.2)], ["US specs"]),
    _listing("ae-003", "Mercedes-Benz E-Class E200 2023", "Mercedes-Benz", "E-Class", "E200", "Sedan", 179000, 2023, 47000, "Dubai", "Dealer", "GCC", "White", 18, [ConditionEvidence(claim="Inspection report available", evidence="Inspection report", confidence=.88)], ["GCC specs", "Warranty"]),
    _listing("ae-004", "Toyota Land Cruiser GXR 2022", "Toyota", "Land Cruiser", "GXR", "SUV", 235000, 2022, 51000, "Dubai", "Dealer", "GCC", "White", 5, [ConditionEvidence(claim="Service history claimed", evidence="Full service history", confidence=.72)], ["GCC specs", "7 seats", "Warranty"]),
    _listing("ae-005", "Toyota Land Cruiser VXR 2021", "Toyota", "Land Cruiser", "VXR", "SUV", 210000, 2021, 73000, "Sharjah", "Private", "GCC", "Black", 26, [ConditionEvidence(claim="Condition not stated", confidence=.2)], ["GCC specs", "7 seats"]),
    _listing("ae-006", "Nissan Patrol Platinum 2022", "Nissan", "Patrol", "Platinum", "SUV", 169000, 2022, 64000, "Dubai", "Dealer", "GCC", "Grey", 8, [ConditionEvidence(claim="Listing claims accident-free", evidence="No accidents", confidence=.64)], ["GCC specs", "7 seats", "Warranty"]),
    _listing("ae-007", "Nissan Patrol SE 2021", "Nissan", "Patrol", "SE", "SUV", 121000, 2021, 89000, "Abu Dhabi", "Private", "GCC", "White", 31, [ConditionEvidence(claim="Condition not stated", confidence=.2)], ["GCC specs", "7 seats"]),
    _listing("ae-008", "BMW X5 xDrive40i 2022", "BMW", "X5", "xDrive40i", "SUV", 198000, 2022, 44000, "Dubai", "Dealer", "GCC", "Blue", 14, [ConditionEvidence(claim="Warranty stated", evidence="Dealer warranty", confidence=.73)], ["GCC specs", "Warranty", "Panoramic roof"]),
    _listing("ae-009", "Lexus RX 350 Premium 2023", "Lexus", "RX", "Premium", "SUV", 219000, 2023, 19000, "Dubai", "Dealer", "GCC", "White", 2, [ConditionEvidence(claim="Inspection report available", confidence=.86)], ["GCC specs", "Warranty", "Panoramic roof"]),
    _listing("ae-010", "Porsche Cayenne 2021", "Porsche", "Cayenne", "Standard", "SUV", 249000, 2021, 58000, "Dubai", "Dealer", "GCC", "Black", 22, [ConditionEvidence(claim="Service history claimed", confidence=.7)], ["GCC specs", "Warranty"]),
]


def _with_market_value(listings: list[CatalogueListing]) -> list[CatalogueListing]:
    output: list[CatalogueListing] = []
    for item in listings:
        comparable = [other.price for other in listings if other.make == item.make and other.model == item.model and abs(other.year - item.year) <= 1 and other.regional_specs == item.regional_specs]
        typical = round(median(comparable)) if comparable else None
        difference = typical - item.price if typical else None
        label = "Fair price"
        if difference and difference > typical * .12: label = "Great deal"
        elif difference and difference > typical * .04: label = "Good deal"
        elif difference and difference < -(typical * .18): label = "Verify price"
        output.append(item.model_copy(update={"typical_price": typical, "deal_difference": difference, "deal_label": label}))
    return output


VALUED_CATALOGUE = _with_market_value(CATALOGUE)


def search_catalogue(filters: ListingFilters) -> tuple[list[CatalogueListing], int]:
    items = [listing for listing in VALUED_CATALOGUE if listing.market == filters.market]
    search = (filters.query or "").casefold()
    if search: items = [item for item in items if search in f"{item.title} {item.make} {item.model} {item.body_type}".casefold()]
    for attribute, value in (("make", filters.make), ("model", filters.model), ("body_type", filters.body_type), ("regional_specs", filters.specs), ("seller_type", filters.seller_type)):
        if value: items = [item for item in items if str(getattr(item, attribute, "")).casefold() == value.casefold()]
    if filters.year_min: items = [item for item in items if item.year >= filters.year_min]
    if filters.year_max: items = [item for item in items if item.year <= filters.year_max]
    if filters.price_max: items = [item for item in items if item.price <= filters.price_max]
    if filters.mileage_max_km: items = [item for item in items if item.mileage_km <= filters.mileage_max_km]
    if filters.sort == "price_low": items.sort(key=lambda item: item.price)
    elif filters.sort == "price_high": items.sort(key=lambda item: item.price, reverse=True)
    elif filters.sort == "mileage_low": items.sort(key=lambda item: item.mileage_km)
    elif filters.sort == "newest": items.sort(key=lambda item: item.freshness_hours)
    else: items.sort(key=lambda item: (item.deal_label != "Great deal", -(item.deal_difference or 0), item.price))
    return items[(filters.page - 1) * filters.page_size: filters.page * filters.page_size], len(items)


def get_listing(listing_id: str) -> CatalogueListing | None:
    return next((listing for listing in VALUED_CATALOGUE if listing.id == listing_id), None)


def catalogue_filters() -> dict[str, list[str]]:
    return {"makes": sorted({item.make for item in VALUED_CATALOGUE}), "body_types": sorted({item.body_type for item in VALUED_CATALOGUE}), "specs": sorted({item.regional_specs for item in VALUED_CATALOGUE if item.regional_specs}), "seller_types": sorted({item.seller_type for item in VALUED_CATALOGUE})}
