from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import cast
from urllib.parse import parse_qsl, urlencode
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from carveo_core.buyer import InvalidSavedSearchQueryError, UnknownListingError
from carveo_core.buyer_contracts import (
    AnonymousWorkspaceMergeRequest,
    BuyerWorkspace,
    Conversation,
    ConversationCreate,
    ConversationSummary,
    ConversationTurn,
    ConversationTurnCreate,
    SavedSearch,
    SavedSearchUpsert,
    WorkspaceMergeResponse,
)
from carveo_core.models import (
    BuyerComparisonItemRecord,
    BuyerConversationRecord,
    BuyerConversationTurnRecord,
    BuyerProfileRecord,
    BuyerSavedSearchRecord,
    BuyerShortlistItemRecord,
    ListingRecord,
)

_MAX_COMPARISON_ITEMS = 4
_MAX_SAVED_SEARCHES = 12


def _canonical_query(query: str) -> str:
    pairs = parse_qsl(query.removeprefix("?"), keep_blank_values=True)
    canonical_query = urlencode(sorted(pairs))
    if not canonical_query:
        raise InvalidSavedSearchQueryError()
    return canonical_query


def _utc(value: datetime) -> datetime:
    return value.astimezone(UTC)


def _saved_search(record: BuyerSavedSearchRecord) -> SavedSearch:
    return SavedSearch(
        id=record.id,
        label=record.label,
        query=record.query,
        created_at=_utc(record.created_at),
        updated_at=_utc(record.updated_at),
    )


def _conversation_summary(record: BuyerConversationRecord) -> ConversationSummary:
    return ConversationSummary(
        id=record.id,
        title=record.title,
        status=record.status,  # type: ignore[arg-type]
        updated_at=_utc(record.updated_at),
    )


class SqlAlchemyBuyerWorkspaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_or_create_profile(self, clerk_user_id: str) -> BuyerProfileRecord:
        statement = (
            insert(BuyerProfileRecord)
            .values(clerk_user_id=clerk_user_id)
            .on_conflict_do_nothing(index_elements=[BuyerProfileRecord.clerk_user_id])
            .returning(BuyerProfileRecord)
        )
        profile = await self._session.scalar(statement)
        if profile is None:
            profile = await self._session.scalar(
                select(BuyerProfileRecord).where(BuyerProfileRecord.clerk_user_id == clerk_user_id)
            )
        if profile is None:
            raise RuntimeError("Buyer profile could not be created")
        return profile

    async def _lock_profile(self, clerk_user_id: str) -> BuyerProfileRecord:
        profile = await self._get_or_create_profile(clerk_user_id)
        locked = await self._session.scalar(
            select(BuyerProfileRecord)
            .where(BuyerProfileRecord.id == profile.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if locked is None:
            raise RuntimeError("Buyer profile disappeared while being locked")
        return locked

    async def _resolve_listings(self, public_ids: list[str]) -> tuple[list[ListingRecord], list[str]]:
        if not public_ids:
            return [], []
        statement = select(ListingRecord).where(ListingRecord.public_id.in_(dict.fromkeys(public_ids)))
        records_by_public_id = {record.public_id: record for record in await self._session.scalars(statement)}
        records = [records_by_public_id[public_id] for public_id in public_ids if public_id in records_by_public_id]
        unknown = [public_id for public_id in public_ids if public_id not in records_by_public_id]
        return records, unknown

    async def _to_workspace(self, profile: BuyerProfileRecord) -> BuyerWorkspace:
        shortlist_statement = (
            select(ListingRecord.public_id)
            .join(BuyerShortlistItemRecord, BuyerShortlistItemRecord.listing_id == ListingRecord.id)
            .where(BuyerShortlistItemRecord.buyer_profile_id == profile.id)
            .order_by(BuyerShortlistItemRecord.created_at, BuyerShortlistItemRecord.id)
        )
        comparison_statement = (
            select(ListingRecord.public_id)
            .join(BuyerComparisonItemRecord, BuyerComparisonItemRecord.listing_id == ListingRecord.id)
            .where(BuyerComparisonItemRecord.buyer_profile_id == profile.id)
            .order_by(BuyerComparisonItemRecord.position)
        )
        saved_search_statement = (
            select(BuyerSavedSearchRecord)
            .where(BuyerSavedSearchRecord.buyer_profile_id == profile.id)
            .order_by(
                BuyerSavedSearchRecord.updated_at.desc(),
                BuyerSavedSearchRecord.created_at.desc(),
                BuyerSavedSearchRecord.id.desc(),
            )
        )
        conversation_statement = (
            select(BuyerConversationRecord)
            .where(BuyerConversationRecord.buyer_profile_id == profile.id)
            .order_by(
                BuyerConversationRecord.updated_at.desc(),
                BuyerConversationRecord.created_at.desc(),
                BuyerConversationRecord.id.desc(),
            )
        )
        shortlist = list(await self._session.scalars(shortlist_statement))
        comparison = list(await self._session.scalars(comparison_statement))
        saved_searches = [_saved_search(record) for record in await self._session.scalars(saved_search_statement)]
        conversations = [
            _conversation_summary(record) for record in await self._session.scalars(conversation_statement)
        ]
        return BuyerWorkspace(
            shortlist_listing_ids=shortlist,
            comparison_listing_ids=comparison,
            saved_searches=saved_searches,
            conversations=conversations,
            anonymous_merged_at=(
                None if profile.anonymous_merged_at is None else _utc(profile.anonymous_merged_at)
            ),
        )

    async def _to_conversation(self, record: BuyerConversationRecord) -> Conversation:
        statement = (
            select(BuyerConversationTurnRecord)
            .where(BuyerConversationTurnRecord.conversation_id == record.id)
            .order_by(BuyerConversationTurnRecord.sequence)
        )
        turns = [
            ConversationTurn(
                id=turn.id,
                sequence=turn.sequence,
                role=turn.role,  # type: ignore[arg-type]
                content=turn.content,
                created_at=_utc(turn.created_at),
            )
            for turn in await self._session.scalars(statement)
        ]
        return Conversation(
            id=record.id,
            title=record.title,
            status=record.status,  # type: ignore[arg-type]
            updated_at=_utc(record.updated_at),
            client_id=record.client_id,
            interpreted_intent=record.interpreted_intent,
            created_at=_utc(record.created_at),
            turns=turns,
        )

    async def _insert_shortlist(self, profile_id: UUID, listings: list[ListingRecord]) -> None:
        created_at = datetime.now(UTC)
        for index, listing in enumerate(listings):
            await self._session.execute(
                insert(BuyerShortlistItemRecord)
                .values(
                    buyer_profile_id=profile_id,
                    listing_id=listing.id,
                    created_at=created_at + timedelta(microseconds=index),
                )
                .on_conflict_do_nothing(
                    index_elements=[
                        BuyerShortlistItemRecord.buyer_profile_id,
                        BuyerShortlistItemRecord.listing_id,
                    ]
                )
            )

    async def _replace_comparison(self, profile_id: UUID, listings: list[ListingRecord]) -> None:
        await self._session.execute(
            delete(BuyerComparisonItemRecord).where(BuyerComparisonItemRecord.buyer_profile_id == profile_id)
        )
        self._session.add_all(
            BuyerComparisonItemRecord(
                buyer_profile_id=profile_id,
                listing_id=listing.id,
                position=position,
            )
            for position, listing in enumerate(listings)
        )

    async def _find_conversation(self, clerk_user_id: str, conversation_id: UUID) -> BuyerConversationRecord | None:
        return cast(
            BuyerConversationRecord | None,
            await self._session.scalar(
                select(BuyerConversationRecord)
                .join(BuyerProfileRecord, BuyerProfileRecord.id == BuyerConversationRecord.buyer_profile_id)
                .where(
                    BuyerConversationRecord.id == conversation_id,
                    BuyerProfileRecord.clerk_user_id == clerk_user_id,
                )
            )
        )

    async def get_workspace(self, clerk_user_id: str) -> BuyerWorkspace:
        async with self._session.begin():
            profile = await self._get_or_create_profile(clerk_user_id)
            return await self._to_workspace(profile)

    async def add_shortlist(self, clerk_user_id: str, listing_public_id: str) -> BuyerWorkspace:
        async with self._session.begin():
            profile = await self._get_or_create_profile(clerk_user_id)
            listings, unknown = await self._resolve_listings([listing_public_id])
            if unknown:
                raise UnknownListingError(unknown)
            await self._insert_shortlist(profile.id, listings)
            return await self._to_workspace(profile)

    async def remove_shortlist(self, clerk_user_id: str, listing_public_id: str) -> BuyerWorkspace:
        async with self._session.begin():
            profile = await self._get_or_create_profile(clerk_user_id)
            listings, unknown = await self._resolve_listings([listing_public_id])
            if unknown:
                raise UnknownListingError(unknown)
            await self._session.execute(
                delete(BuyerShortlistItemRecord).where(
                    BuyerShortlistItemRecord.buyer_profile_id == profile.id,
                    BuyerShortlistItemRecord.listing_id == listings[0].id,
                )
            )
            return await self._to_workspace(profile)

    async def replace_comparison(self, clerk_user_id: str, listing_public_ids: list[str]) -> BuyerWorkspace:
        if len(listing_public_ids) > _MAX_COMPARISON_ITEMS or len(listing_public_ids) != len(set(listing_public_ids)):
            raise ValueError("Comparison listing IDs must be unique and contain at most four values")
        async with self._session.begin():
            profile = await self._lock_profile(clerk_user_id)
            listings, unknown = await self._resolve_listings(listing_public_ids)
            if unknown:
                raise UnknownListingError(unknown)
            await self._replace_comparison(profile.id, listings)
            await self._session.flush()
            return await self._to_workspace(profile)

    async def upsert_saved_search(self, clerk_user_id: str, payload: SavedSearchUpsert) -> SavedSearch:
        query = _canonical_query(payload.query)
        async with self._session.begin():
            profile = await self._lock_profile(clerk_user_id)
            existing = await self._session.scalar(
                select(BuyerSavedSearchRecord).where(
                    BuyerSavedSearchRecord.buyer_profile_id == profile.id,
                    BuyerSavedSearchRecord.query == query,
                )
            )
            if existing is not None:
                existing.label = payload.label
                existing.updated_at = datetime.now(UTC)
                await self._session.flush()
                return _saved_search(existing)

            count = await self._session.scalar(
                select(func.count())
                .select_from(BuyerSavedSearchRecord)
                .where(BuyerSavedSearchRecord.buyer_profile_id == profile.id)
            )
            if (count or 0) >= _MAX_SAVED_SEARCHES:
                oldest_id = await self._session.scalar(
                    select(BuyerSavedSearchRecord.id)
                    .where(BuyerSavedSearchRecord.buyer_profile_id == profile.id)
                    .order_by(
                        BuyerSavedSearchRecord.updated_at,
                        BuyerSavedSearchRecord.created_at,
                        BuyerSavedSearchRecord.id,
                    )
                    .limit(1)
                )
                if oldest_id is not None:
                    await self._session.execute(
                        delete(BuyerSavedSearchRecord).where(BuyerSavedSearchRecord.id == oldest_id)
                    )
            record = BuyerSavedSearchRecord(
                buyer_profile_id=profile.id,
                label=payload.label,
                query=query,
            )
            self._session.add(record)
            await self._session.flush()
            return _saved_search(record)

    async def delete_saved_search(self, clerk_user_id: str, saved_search_id: UUID) -> bool:
        async with self._session.begin():
            profile_id = select(BuyerProfileRecord.id).where(BuyerProfileRecord.clerk_user_id == clerk_user_id)
            deleted_id = await self._session.scalar(
                delete(BuyerSavedSearchRecord)
                .where(
                    BuyerSavedSearchRecord.id == saved_search_id,
                    BuyerSavedSearchRecord.buyer_profile_id == profile_id.scalar_subquery(),
                )
                .returning(BuyerSavedSearchRecord.id)
            )
            return deleted_id is not None

    async def list_conversations(self, clerk_user_id: str) -> list[ConversationSummary]:
        async with self._session.begin():
            profile = await self._get_or_create_profile(clerk_user_id)
            records = await self._session.scalars(
                select(BuyerConversationRecord)
                .where(BuyerConversationRecord.buyer_profile_id == profile.id)
                .order_by(
                    BuyerConversationRecord.updated_at.desc(),
                    BuyerConversationRecord.created_at.desc(),
                    BuyerConversationRecord.id.desc(),
                )
            )
            return [_conversation_summary(record) for record in records]

    async def create_conversation(self, clerk_user_id: str, payload: ConversationCreate) -> Conversation:
        async with self._session.begin():
            profile = await self._lock_profile(clerk_user_id)
            existing = await self._session.scalar(
                select(BuyerConversationRecord).where(
                    BuyerConversationRecord.buyer_profile_id == profile.id,
                    BuyerConversationRecord.client_id == payload.client_id,
                )
            )
            if existing is not None:
                return await self._to_conversation(existing)
            record = BuyerConversationRecord(
                buyer_profile_id=profile.id,
                client_id=payload.client_id,
                title=payload.title,
                interpreted_intent=payload.interpreted_intent,
            )
            self._session.add(record)
            await self._session.flush()
            self._session.add_all(
                BuyerConversationTurnRecord(
                    conversation_id=record.id,
                    sequence=sequence,
                    role=turn.role,
                    content=turn.content,
                )
                for sequence, turn in enumerate(payload.turns)
            )
            await self._session.flush()
            return await self._to_conversation(record)

    async def get_conversation(self, clerk_user_id: str, conversation_id: UUID) -> Conversation | None:
        async with self._session.begin():
            record = await self._find_conversation(clerk_user_id, conversation_id)
            return None if record is None else await self._to_conversation(record)

    async def append_turn(
        self,
        clerk_user_id: str,
        conversation_id: UUID,
        payload: ConversationTurnCreate,
    ) -> Conversation | None:
        async with self._session.begin():
            record = await self._session.scalar(
                select(BuyerConversationRecord)
                .join(BuyerProfileRecord, BuyerProfileRecord.id == BuyerConversationRecord.buyer_profile_id)
                .where(
                    BuyerConversationRecord.id == conversation_id,
                    BuyerProfileRecord.clerk_user_id == clerk_user_id,
                )
                .with_for_update()
            )
            if record is None:
                return None
            latest_sequence = await self._session.scalar(
                select(func.max(BuyerConversationTurnRecord.sequence)).where(
                    BuyerConversationTurnRecord.conversation_id == record.id
                )
            )
            self._session.add(
                BuyerConversationTurnRecord(
                    conversation_id=record.id,
                    sequence=0 if latest_sequence is None else latest_sequence + 1,
                    role=payload.role,
                    content=payload.content,
                )
            )
            record.updated_at = datetime.now(UTC)
            await self._session.flush()
            return await self._to_conversation(record)

    async def merge_anonymous(
        self,
        clerk_user_id: str,
        payload: AnonymousWorkspaceMergeRequest,
    ) -> WorkspaceMergeResponse:
        async with self._session.begin():
            profile = await self._lock_profile(clerk_user_id)
            if profile.anonymous_merged_at is not None:
                return WorkspaceMergeResponse(
                    workspace=await self._to_workspace(profile),
                    merged=False,
                    ignored_listing_ids=[],
                )

            shortlist, missing_shortlist = await self._resolve_listings(payload.shortlist_listing_ids)
            comparison, missing_comparison = await self._resolve_listings(payload.comparison_listing_ids)
            await self._insert_shortlist(profile.id, shortlist)

            current_comparison = list(
                await self._session.scalars(
                    select(ListingRecord)
                    .join(BuyerComparisonItemRecord, BuyerComparisonItemRecord.listing_id == ListingRecord.id)
                    .where(BuyerComparisonItemRecord.buyer_profile_id == profile.id)
                    .order_by(BuyerComparisonItemRecord.position)
                )
            )
            merged_comparison: list[ListingRecord] = []
            seen_listing_ids: set[UUID] = set()
            for listing in [*current_comparison, *comparison]:
                if listing.id not in seen_listing_ids and len(merged_comparison) < _MAX_COMPARISON_ITEMS:
                    merged_comparison.append(listing)
                    seen_listing_ids.add(listing.id)
            await self._replace_comparison(profile.id, merged_comparison)

            saved_queries = set(
                await self._session.scalars(
                    select(BuyerSavedSearchRecord.query).where(BuyerSavedSearchRecord.buyer_profile_id == profile.id)
                )
            )
            saved_slots = _MAX_SAVED_SEARCHES - len(saved_queries)
            saved_at = datetime.now(UTC)
            for index, saved_search in enumerate(payload.saved_searches):
                query = _canonical_query(saved_search.query)
                if query in saved_queries or saved_slots == 0:
                    continue
                self._session.add(
                    BuyerSavedSearchRecord(
                        buyer_profile_id=profile.id,
                        label=saved_search.label,
                        query=query,
                        created_at=saved_at - timedelta(microseconds=index),
                        updated_at=saved_at - timedelta(microseconds=index),
                    )
                )
                saved_queries.add(query)
                saved_slots -= 1

            conversation_client_ids = set(
                await self._session.scalars(
                    select(BuyerConversationRecord.client_id).where(
                        BuyerConversationRecord.buyer_profile_id == profile.id
                    )
                )
            )
            conversation_at = datetime.now(UTC)
            for index, conversation in enumerate(payload.conversations):
                if conversation.client_id in conversation_client_ids:
                    continue
                record = BuyerConversationRecord(
                    buyer_profile_id=profile.id,
                    client_id=conversation.client_id,
                    title=conversation.title,
                    interpreted_intent=conversation.interpreted_intent,
                    created_at=conversation_at - timedelta(microseconds=index),
                    updated_at=conversation_at - timedelta(microseconds=index),
                )
                self._session.add(record)
                await self._session.flush()
                self._session.add_all(
                    BuyerConversationTurnRecord(
                        conversation_id=record.id,
                        sequence=sequence,
                        role=turn.role,
                        content=turn.content,
                    )
                    for sequence, turn in enumerate(conversation.turns)
                )
                conversation_client_ids.add(conversation.client_id)

            profile.anonymous_merged_at = datetime.now(UTC)
            await self._session.flush()
            ignored = list(dict.fromkeys([*missing_shortlist, *missing_comparison]))
            return WorkspaceMergeResponse(
                workspace=await self._to_workspace(profile),
                merged=True,
                ignored_listing_ids=ignored,
            )
