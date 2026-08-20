import pytest
from carveo_core.catalogue import FixtureCatalogueRepository
from carveo_core.contracts import CompareRequest, ListingQuery
from carveo_core.fixtures import load_fixture_listings


@pytest.fixture
def repository() -> FixtureCatalogueRepository:
    return FixtureCatalogueRepository(load_fixture_listings())


@pytest.mark.anyio
async def test_filters_sorts_and_paginates(repository: FixtureCatalogueRepository) -> None:
    result = await repository.search(
        ListingQuery(
            make=["Toyota"],
            body_type=["SUV"],
            specifications=["GCC"],
            sort="lowest-price",
            page=1,
            page_size=12,
        )
    )

    assert result.total >= 2
    assert all(item.make == "Toyota" and item.body_type == "SUV" for item in result.items)
    assert [item.price for item in result.items] == sorted(item.price for item in result.items)
    assert all(item.deal_position is not None for item in result.items)


@pytest.mark.anyio
async def test_stated_evidence_matches_positive_and_warning_claims(
    repository: FixtureCatalogueRepository,
) -> None:
    result = await repository.search(ListingQuery(evidence=["stated"], page_size=48))

    assert result.items
    assert all(
        any(claim.kind in {"positive", "warning"} for claim in item.condition_evidence)
        for item in result.items
    )


@pytest.mark.anyio
async def test_compare_preserves_order_and_reports_missing(
    repository: FixtureCatalogueRepository,
) -> None:
    response = await repository.compare(
        CompareRequest(
            listing_ids=[
                "cv-toyota-rav4-2021-02",
                "missing",
                "cv-toyota-land-cruiser-2022-01",
            ]
        )
    )

    assert [item.id for item in response.items] == [
        "cv-toyota-rav4-2021-02",
        "cv-toyota-land-cruiser-2022-01",
    ]
    assert response.missing_ids == ["missing"]


def test_query_rejects_invalid_range() -> None:
    with pytest.raises(ValueError, match="yearMin"):
        ListingQuery(year_min=2025, year_max=2020)
