from carveo_core.fixtures import load_fixture_listings


def test_canonical_fixture_dataset_builds_24_valid_listings() -> None:
    listings = load_fixture_listings()

    assert len(listings) == 24
    assert len({listing.id for listing in listings}) == 24
    assert {listing.market for listing in listings} == {"ae"}
    assert all(listing.photos for listing in listings)


def test_fixture_dataset_preserves_unknown_condition_evidence() -> None:
    listings = load_fixture_listings()

    unknown = [listing for listing in listings if listing.condition_evidence[0].kind == "unknown"]
    assert unknown
    assert all(item.condition_evidence[0].label == "Condition not stated" for item in unknown)
