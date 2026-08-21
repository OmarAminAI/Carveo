from datetime import UTC, datetime, timedelta, timezone
from uuid import uuid4

import pytest
from carveo_core.buyer_contracts import (
    BuyerWorkspace,
    ComparisonUpdate,
    Conversation,
    ConversationCreate,
    ConversationSummary,
    ConversationTurn,
    ConversationTurnCreate,
    SavedSearch,
    SavedSearchUpsert,
)
from carveo_core.models import Base
from pydantic import ValidationError


def test_catalogue_metadata_contains_expected_tables() -> None:
    assert set(Base.metadata.tables) == {
        "buyer_comparison_items",
        "buyer_conversation_turns",
        "buyer_conversations",
        "buyer_profiles",
        "buyer_saved_searches",
        "buyer_shortlist_items",
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


def test_buyer_metadata_enforces_ownership_and_ordering_constraints() -> None:
    profile = Base.metadata.tables["buyer_profiles"]
    shortlist = Base.metadata.tables["buyer_shortlist_items"]
    comparison = Base.metadata.tables["buyer_comparison_items"]
    saved_search = Base.metadata.tables["buyer_saved_searches"]
    conversation = Base.metadata.tables["buyer_conversations"]
    turn = Base.metadata.tables["buyer_conversation_turns"]

    assert {"clerk_user_id"} in _unique_column_sets(profile)
    assert {"buyer_profile_id", "listing_id"} in _unique_column_sets(shortlist)
    assert {"buyer_profile_id", "listing_id"} in _unique_column_sets(comparison)
    assert {"buyer_profile_id", "position"} in _unique_column_sets(comparison)
    assert {"buyer_profile_id", "query"} in _unique_column_sets(saved_search)
    assert {"buyer_profile_id", "client_id"} in _unique_column_sets(conversation)
    assert {"conversation_id", "sequence"} in _unique_column_sets(turn)

    assert _foreign_key_targets(shortlist) == {"buyer_profiles.id", "listings.id"}
    assert _foreign_key_targets(comparison) == {"buyer_profiles.id", "listings.id"}
    assert _foreign_key_targets(saved_search) == {"buyer_profiles.id"}
    assert _foreign_key_targets(conversation) == {"buyer_profiles.id"}
    assert _foreign_key_targets(turn) == {"buyer_conversations.id"}

    assert {"ix_buyer_profiles_clerk_user_id"} <= _index_names(profile)
    assert {"ix_buyer_shortlist_items_buyer_profile_id"} <= _index_names(shortlist)
    assert {"ix_buyer_comparison_items_buyer_profile_id"} <= _index_names(comparison)
    assert {"ix_buyer_saved_searches_profile_updated_at"} <= _index_names(saved_search)
    assert {"ix_buyer_conversations_profile_updated_at"} <= _index_names(conversation)
    assert {"ix_buyer_conversation_turns_conversation_sequence"} <= _index_names(turn)
    assert {"ck_buyer_comparison_items_position"} <= _check_constraint_names(comparison)
    assert {"ck_buyer_conversations_status"} <= _check_constraint_names(conversation)
    assert {"ck_buyer_conversation_turns_role", "ck_buyer_conversation_turns_sequence"} <= _check_constraint_names(turn)


def test_buyer_contracts_are_camel_case_and_bound_untrusted_input() -> None:
    saved_search = SavedSearch(
        id=uuid4(),
        label="Dubai SUVs",
        query="make=Toyota",
        created_at=datetime(2026, 8, 21, tzinfo=UTC),
        updated_at=datetime(2026, 8, 21, tzinfo=UTC),
    )
    turn = ConversationTurn(
        id=uuid4(),
        sequence=0,
        role="buyer",
        content="Find a Land Cruiser",
        created_at=datetime(2026, 8, 21, tzinfo=UTC),
    )
    summary = ConversationSummary(
        id=uuid4(),
        title="Family SUV",
        status="active",
        updated_at=datetime(2026, 8, 21, tzinfo=UTC),
    )
    conversation = Conversation(
        **summary.model_dump(),
        client_id="browser-conversation-1",
        interpreted_intent={"make": "Toyota"},
        created_at=datetime(2026, 8, 21, tzinfo=UTC),
        turns=[turn],
    )
    workspace = BuyerWorkspace(
        shortlist_listing_ids=["listing-1"],
        comparison_listing_ids=["listing-2"],
        saved_searches=[saved_search],
        conversations=[summary],
        anonymous_merged_at=None,
    )

    assert workspace.model_dump(by_alias=True)["shortlistListingIds"] == ["listing-1"]
    assert conversation.model_dump(by_alias=True)["interpretedIntent"] == {"make": "Toyota"}

    with pytest.raises(ValidationError):
        ComparisonUpdate(listing_ids=["listing-1", "listing-1"])
    with pytest.raises(ValidationError):
        ComparisonUpdate(listing_ids=["1", "2", "3", "4", "5"])
    with pytest.raises(ValidationError):
        SavedSearchUpsert(label="x" * 121, query="make=Toyota")
    with pytest.raises(ValidationError):
        ConversationCreate(client_id="x" * 101, title="Family SUV")
    with pytest.raises(ValidationError):
        ConversationTurnCreate(role="buyer", content="x" * 8001)


def test_buyer_workspace_rejects_more_than_four_comparison_listing_ids() -> None:
    with pytest.raises(ValidationError):
        BuyerWorkspace(comparison_listing_ids=["1", "2", "3", "4", "5"])


def test_buyer_workspace_rejects_duplicate_comparison_listing_ids() -> None:
    with pytest.raises(ValidationError):
        BuyerWorkspace(comparison_listing_ids=["listing-1", "listing-1"])


def test_buyer_contracts_reject_naive_timestamps() -> None:
    naive_timestamp = datetime(2026, 8, 21)
    utc_timestamp = datetime(2026, 8, 21, tzinfo=UTC)

    with pytest.raises(ValidationError):
        SavedSearch(
            id=uuid4(),
            label="Dubai SUVs",
            query="make=Toyota",
            created_at=naive_timestamp,
            updated_at=utc_timestamp,
        )
    with pytest.raises(ValidationError):
        SavedSearch(
            id=uuid4(),
            label="Dubai SUVs",
            query="make=Toyota",
            created_at=utc_timestamp,
            updated_at=naive_timestamp,
        )
    with pytest.raises(ValidationError):
        ConversationSummary(
            id=uuid4(),
            title="Family SUV",
            status="active",
            updated_at=naive_timestamp,
        )
    with pytest.raises(ValidationError):
        ConversationTurn(
            id=uuid4(),
            sequence=0,
            role="buyer",
            content="Find a Land Cruiser",
            created_at=naive_timestamp,
        )
    with pytest.raises(ValidationError):
        Conversation(
            id=uuid4(),
            title="Family SUV",
            status="active",
            updated_at=utc_timestamp,
            client_id="browser-conversation-1",
            created_at=naive_timestamp,
        )
    with pytest.raises(ValidationError):
        BuyerWorkspace(anonymous_merged_at=naive_timestamp)


def test_buyer_contracts_reject_non_utc_timestamps() -> None:
    with pytest.raises(ValidationError):
        ConversationTurn(
            id=uuid4(),
            sequence=0,
            role="buyer",
            content="Find a Land Cruiser",
            created_at=datetime(2026, 8, 21, tzinfo=timezone(timedelta(hours=2))),
        )


def _unique_column_sets(table: object) -> list[set[str]]:
    return [
        {column.name for column in constraint.columns}
        for constraint in table.constraints  # type: ignore[union-attr]
        if hasattr(constraint, "columns") and constraint.__class__.__name__ == "UniqueConstraint"
    ]


def _foreign_key_targets(table: object) -> set[str]:
    return {
        foreign_key.target_fullname
        for column in table.columns  # type: ignore[union-attr]
        for foreign_key in column.foreign_keys
    }


def _index_names(table: object) -> set[str]:
    return {index.name for index in table.indexes}  # type: ignore[union-attr]


def _check_constraint_names(table: object) -> set[str]:
    return {
        constraint.name
        for constraint in table.constraints  # type: ignore[union-attr]
        if constraint.__class__.__name__ == "CheckConstraint"
    }
