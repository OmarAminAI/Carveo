from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import SearchMessageRecord, SearchSessionRecord
from app.db.session import get_db
from app.schemas.search import (
    ChatMessage,
    CreateSessionResponse,
    SearchIntent,
    SearchResultsResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.services.fixtures import FIXTURE_LISTINGS
from app.services.intent import extract_intent, get_intent_state, merge_intent
from app.services.ranking import rank_listings

router = APIRouter(prefix="/sessions", tags=["search"])


def _get_session(session_id: str, db: Session) -> SearchSessionRecord:
    record = db.get(SearchSessionRecord, session_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search session not found")
    return record


@router.post("", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(db: Session = Depends(get_db)) -> CreateSessionResponse:
    record = SearchSessionRecord(intent=SearchIntent().model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return CreateSessionResponse(session_id=record.id, intent_state=get_intent_state(SearchIntent()))


@router.post("/{session_id}/messages", response_model=SendMessageResponse)
def send_message(session_id: str, request: SendMessageRequest, db: Session = Depends(get_db)) -> SendMessageResponse:
    record = _get_session(session_id, db)
    current_intent = SearchIntent.model_validate(record.intent or {})
    updated_intent = merge_intent(current_intent, extract_intent(request.content))
    state = get_intent_state(updated_intent)
    assistant_content = (
        "Your search is ready. I found fixture listings while live Dubizzle ingestion is being prepared."
        if state.ready
        else state.next_question or "Tell me more about the car you want."
    )
    record.intent = updated_intent.model_dump()
    db.add_all(
        [
            SearchMessageRecord(session_id=record.id, role="user", content=request.content),
            SearchMessageRecord(session_id=record.id, role="assistant", content=assistant_content),
        ]
    )
    db.commit()
    return SendMessageResponse(
        session_id=record.id,
        message=ChatMessage(role="assistant", content=assistant_content),
        intent_state=state,
    )


@router.get("/{session_id}/results", response_model=SearchResultsResponse)
def get_results(session_id: str, db: Session = Depends(get_db)) -> SearchResultsResponse:
    record = _get_session(session_id, db)
    intent = SearchIntent.model_validate(record.intent or {})
    state = get_intent_state(intent)
    if not state.ready:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Search is not ready", "missing_fields": state.missing_fields},
        )
    return SearchResultsResponse(session_id=record.id, intent=intent, matches=rank_listings(intent, FIXTURE_LISTINGS))

