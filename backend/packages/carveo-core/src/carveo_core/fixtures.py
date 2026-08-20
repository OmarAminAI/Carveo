import json
from datetime import datetime
from importlib.resources import files

from pydantic import TypeAdapter

from carveo_core.contracts import (
    ConditionEvidence,
    DuplicateOffer,
    FixtureSeed,
    Listing,
    PriceObservation,
    SourceAttribution,
)

_seed_adapter = TypeAdapter(list[FixtureSeed])


def _datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


_media_by_body_type = {
    "SUV": "/media/fixture-suv.jpg",
    "Sedan": "/media/fixture-sedan.jpg",
    "Coupe": "/media/fixture-coupe.jpg",
    "Hatchback": "/media/fixture-hatchback.jpg",
    "Pickup": "/media/fixture-pickup.jpg",
    "Convertible": "/media/fixture-convertible.jpg",
}
_media_by_model = {
    "Toyota Land Cruiser": "/media/toyota-land-cruiser.jpg",
    "Nissan Patrol": "/media/nissan-patrol.jpg",
    "BMW X5": "/media/bmw-x5.jpg",
    "Mercedes-Benz C 200": "/media/mercedes-c-class.jpg",
}


def load_fixture_seeds() -> list[FixtureSeed]:
    fixture_path = files("carveo_core").joinpath("data/ae-listings.json")
    return _seed_adapter.validate_python(json.loads(fixture_path.read_text(encoding="utf-8")))


def load_fixture_listings() -> list[Listing]:
    listings: list[Listing] = []
    for index, seed in enumerate(load_fixture_seeds()):
        unknown = index % 3 == 1
        warning = index % 7 == 0
        seen_day = f"{(index % 18) + 1:02d}"
        media = _media_by_model.get(f"{seed.make} {seed.model}", _media_by_body_type[seed.body_type])
        if unknown:
            evidence = ConditionEvidence(
                kind="unknown",
                label="Condition not stated",
                detail=("The fixture source does not state accident, damage, service, or inspection history."),
            )
        elif warning:
            evidence = ConditionEvidence(
                kind="warning",
                label="Repair stated",
                detail="The source notes a repainted bumper.",
                source_claim="Rear bumper repainted",
            )
        else:
            evidence = ConditionEvidence(
                kind="positive",
                label="Service history stated",
                detail="The source states service history is available.",
                source_claim="Service history available",
            )
        features = [
            "Climate control",
            "Rear camera",
            "Cruise control" if index % 2 else "Leather seats",
            "Bluetooth" if index % 4 else "Sunroof",
        ]
        duplicates = (
            [
                DuplicateOffer(
                    source="Fixture partner B",
                    price=seed.price + 3_000,
                    url=f"https://fixtures-b.carveo.local/listings/{seed.id}",
                )
            ]
            if index % 6 == 0
            else []
        )
        listings.append(
            Listing(
                **seed.model_dump(),
                market="ae",
                title=f"{seed.year} {seed.make} {seed.model} {seed.trim}",
                currency="AED",
                source=SourceAttribution(
                    name="Carveo approved fixture",
                    listing_url=f"https://fixtures.carveo.local/listings/{seed.id}",
                    status="Fixture",
                ),
                description=(
                    f"Source-stated fixture record for a {seed.year} {seed.make} "
                    f"{seed.model} in {seed.city}. Data is illustrative and not a live advertisement."
                ),
                features=features,
                photos=[media, media],
                first_seen_at=_datetime(f"2026-08-{seen_day}T08:00:00Z"),
                last_seen_at=_datetime(f"2026-08-19T{8 + (index % 9):02d}:00:00Z"),
                condition_evidence=[evidence],
                price_history=[
                    PriceObservation(
                        observed_at=_datetime("2026-07-20T08:00:00Z"),
                        price=round(seed.price * 1.04),
                    ),
                    PriceObservation(observed_at=_datetime("2026-08-19T08:00:00Z"), price=seed.price),
                ],
                duplicate_offers=duplicates,
            )
        )
    return listings
