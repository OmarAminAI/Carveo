from carveo_core.models import Base


def test_catalogue_metadata_contains_expected_tables() -> None:
    assert set(Base.metadata.tables) == {
        "condition_evidence",
        "duplicate_offers",
        "listing_photos",
        "listings",
        "price_observations",
        "sources",
    }

    listing = Base.metadata.tables["listings"]
    assert {"source_id", "source_listing_id"} in [
        {column.name for column in constraint.columns}
        for constraint in listing.constraints
        if hasattr(constraint, "columns")
    ]
