from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    ConversationListResponse,
    MessageCreate,
    MessageResponse,
    MessageListResponse,
)
from backend.app.services import conversation_service as service


router = APIRouter(
    prefix="/api/v1/conversations",
    tags=["Conversations"],
)


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=201,
)
def create(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.create_conversation(
        db, user.id, data.title
    )


@router.get(
    "",
    response_model=ConversationListResponse,
)
def list_all(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.list_conversations(
        db, user.id, limit, offset
    )


@router.delete("", status_code=204)
def clear_all(
    confirm: bool = Query(False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not confirm:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=400,
            detail="Confirmation is required.",
        )

    service.clear_history(db, user.id)

    return Response(status_code=204)


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def get_one(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.get_conversation(
        db, user.id, conversation_id
    )


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
)
def rename(
    conversation_id: UUID,
    data: ConversationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.rename_conversation(
        db, user.id, conversation_id, data.title
    )


@router.delete(
    "/{conversation_id}",
    status_code=204,
)
def remove(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    service.delete_conversation(
        db, user.id, conversation_id
    )

    return Response(status_code=204)


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
def create_message(
    conversation_id: UUID,
    data: MessageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.add_message(
        db=db,
        user_id=user.id,
        conversation_id=conversation_id,
        content=data.content,
        language=data.language,
        role="user",
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=MessageListResponse,
)
def get_messages(
    conversation_id: UUID,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return service.list_messages(
        db, user.id, conversation_id, limit, offset
    )
