from app.schemas.search import SearchIntent
from app.services.fixtures import FIXTURE_LISTINGS
from app.services.ranking import dedupe_listings, rank_listings


def test_ranking_excludes_over_budget_listings() -> None:
    intent = SearchIntent(market="UAE", make="Mercedes-Benz", year_min=2023, year_max=2023, budget_max=175000, colors=["Black"], specifications=["GCC"], condition_preferences=["accident-free"])

    matches = rank_listings(intent, FIXTURE_LISTINGS)

    assert [match.listing.id for match in matches] == ["dubizzle-fixture-1", "dubizzle-fixture-3"]
    assert matches[0].listing.id == "dubizzle-fixture-1"


def test_dedupe_keeps_the_freshest_duplicate() -> None:
    duplicate = FIXTURE_LISTINGS[0].model_copy(update={"id": "duplicate", "freshness_days": 8})

    deduped = dedupe_listings([duplicate, FIXTURE_LISTINGS[0]])

    assert deduped == [FIXTURE_LISTINGS[0]]
