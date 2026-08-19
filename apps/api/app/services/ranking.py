from statistics import median

from app.schemas.search import RankedMatch, SearchIntent, VehicleListing


def rank_listings(intent: SearchIntent, listings: list[VehicleListing]) -> list[RankedMatch]:
    eligible = [listing for listing in dedupe_listings(listings) if _passes_hard_filters(intent, listing)]
    prices = [listing.price for listing in eligible]
    typical_price = median(prices) if len(prices) >= 2 else None
    matches = [_score(intent, listing, typical_price) for listing in eligible]
    return sorted(matches, key=lambda match: match.score, reverse=True)[:10]


def dedupe_listings(listings: list[VehicleListing]) -> list[VehicleListing]:
    """V1 keeps the freshest record for an exact source URL/title duplicate."""
    unique: dict[tuple[str, str], VehicleListing] = {}
    for listing in listings:
        key = (str(listing.source_url), listing.title.casefold())
        current = unique.get(key)
        if current is None or listing.freshness_days < current.freshness_days:
            unique[key] = listing
    return list(unique.values())


def _passes_hard_filters(intent: SearchIntent, listing: VehicleListing) -> bool:
    if intent.make and listing.make.casefold() != intent.make.casefold():
        return False
    if intent.year_min and listing.year < intent.year_min:
        return False
    if intent.year_max and listing.year > intent.year_max:
        return False
    if intent.budget_max and listing.price > intent.budget_max:
        return False
    return True


def _score(intent: SearchIntent, listing: VehicleListing, typical_price: float | None) -> RankedMatch:
    scores = {"intent_fit": 0.0, "price_quality": 0.0, "condition_risk": 0.0, "trust": 0.0, "freshness": 0.0, "location": 0.0, "confidence": 5.0}
    reasons: list[str] = []
    warnings: list[str] = []
    scores["intent_fit"] = 15.0
    if not intent.models or listing.model in intent.models:
        scores["intent_fit"] += 7.0
        reasons.append("Matches your model preference")
    if not intent.colors or listing.color in intent.colors:
        scores["intent_fit"] += 4.0
    if not intent.mileage_max_km or listing.mileage_km <= intent.mileage_max_km:
        scores["intent_fit"] += 4.0
    if typical_price:
        scores["price_quality"] = 25.0 if listing.price <= typical_price else 15.0
    if "accident-free" in intent.condition_preferences and "Listing claims accident-free" in listing.condition_signals:
        scores["condition_risk"] += 16.0
        reasons.append("Listing claims accident-free")
    elif "Imported specs" in listing.condition_signals:
        scores["condition_risk"] += 5.0
        warnings.append("Imported specs; verify history and regional suitability")
    else:
        scores["condition_risk"] += 10.0
    if listing.warranty:
        scores["condition_risk"] += 4.0
        reasons.append("Warranty included")
    scores["trust"] = 8.0 if listing.seller_type == "Dealer" else 4.0
    scores["freshness"] = 5.0 if listing.freshness_days <= 3 else 2.0
    if not intent.city or listing.city.casefold() == intent.city.casefold():
        scores["location"] = 5.0
    score = round(sum(scores.values()), 1)
    return RankedMatch(listing=listing, score=score, score_components=scores, reasons=reasons, warnings=warnings)
