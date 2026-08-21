from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import UUID

from carveo_core.buyer import BuyerWorkspaceRepository
from carveo_core.buyer_contracts import (
    AnonymousWorkspaceMergeRequest,
    BuyerWorkspace,
    ComparisonUpdate,
    Conversation,
    ConversationCreate,
    ConversationSummary,
    ConversationTurnCreate,
    SavedSearch,
    SavedSearchUpsert,
    WorkspaceMergeResponse,
)
from carveo_core.buyer_sql_repository import SqlAlchemyBuyerWorkspaceRepository
from fastapi import APIRouter, Depends, Request, Response

from carveo_api.auth import AuthenticatedBuyer, require_buyer
from carveo_api.problems import problem

router = APIRouter(prefix="/api/v1/me", tags=["buyer"])


async def buyer_repositories(request: Request) -> AsyncIterator[BuyerWorkspaceRepository]:
    injected = request.app.state.buyer_repository
    if injected is not None:
        yield injected
        return
    session_factory = request.app.state.session_factory
    if session_factory is None:
        raise RuntimeError("Database session is unavailable")
    async with session_factory() as session:
        yield SqlAlchemyBuyerWorkspaceRepository(session)


@router.get("/workspace", response_model=BuyerWorkspace)
async def workspace(
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> BuyerWorkspace:
    return await repository.get_workspace(buyer.clerk_user_id)


@router.post("/workspace/merge", response_model=WorkspaceMergeResponse)
async def merge_workspace(
    payload: AnonymousWorkspaceMergeRequest,
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> WorkspaceMergeResponse:
    return await repository.merge_anonymous(buyer.clerk_user_id, payload)


@router.put("/shortlist/{listing_id}", response_model=BuyerWorkspace)
async def add_shortlist(
    listing_id: str,
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> BuyerWorkspace:
    return await repository.add_shortlist(buyer.clerk_user_id, listing_id)


@router.delete("/shortlist/{listing_id}", response_model=BuyerWorkspace)
async def remove_shortlist(
    listing_id: str,
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> BuyerWorkspace:
    return await repository.remove_shortlist(buyer.clerk_user_id, listing_id)


@router.put("/comparison", response_model=BuyerWorkspace)
async def replace_comparison(
    payload: ComparisonUpdate,
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> BuyerWorkspace:
    return await repository.replace_comparison(buyer.clerk_user_id, payload.listing_ids)


@router.get("/saved-searches", response_model=list[SavedSearch])
async def saved_searches(
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> list[SavedSearch]:
    return (await repository.get_workspace(buyer.clerk_user_id)).saved_searches


@router.post("/saved-searches", response_model=SavedSearch)
async def upsert_saved_search(
    payload: SavedSearchUpsert,
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> SavedSearch:
    return await repository.upsert_saved_search(buyer.clerk_user_id, payload)


@router.delete("/saved-searches/{saved_search_id}", status_code=204)
async def delete_saved_search(
    saved_search_id: UUID,
    request: Request,
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> Response:
    if not await repository.delete_saved_search(buyer.clerk_user_id, saved_search_id):
        return problem(
            status=404,
            slug="not-found",
            title="Saved search not found",
            detail="The requested saved search does not exist.",
            instance=request.url.path,
        )
    return Response(status_code=204)


@router.get("/conversations", response_model=list[ConversationSummary])
async def conversations(
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> list[ConversationSummary]:
    return await repository.list_conversations(buyer.clerk_user_id)


@router.post("/conversations", response_model=Conversation)
async def create_conversation(
    payload: ConversationCreate,
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> Conversation:
    return await repository.create_conversation(buyer.clerk_user_id, payload)


@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def conversation_detail(
    conversation_id: UUID,
    request: Request,
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> Conversation | Response:
    conversation = await repository.get_conversation(buyer.clerk_user_id, conversation_id)
    if conversation is None:
        return problem(
            status=404,
            slug="not-found",
            title="Conversation not found",
            detail="The requested conversation does not exist.",
            instance=request.url.path,
        )
    return conversation


@router.post("/conversations/{conversation_id}/turns", response_model=Conversation)
async def append_turn(
    conversation_id: UUID,
    payload: ConversationTurnCreate,
    request: Request,
    buyer: AuthenticatedBuyer = Depends(require_buyer),
    repository: BuyerWorkspaceRepository = Depends(buyer_repositories),
) -> Conversation | Response:
    conversation = await repository.append_turn(buyer.clerk_user_id, conversation_id, payload)
    if conversation is None:
        return problem(
            status=404,
            slug="not-found",
            title="Conversation not found",
            detail="The requested conversation does not exist.",
            instance=request.url.path,
        )
    return conversation
