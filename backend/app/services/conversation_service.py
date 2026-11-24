from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.user import User, UserPreferences


def require_history_enabled(
    db: Session,
    user_id: UUID,
) -> None:

    db.execute(
        select(User.id)
        .where(User.id == user_id)
        .with_for_update()
    )

    preferences = db.scalar(
        select(UserPreferences)
        .where(UserPreferences.user_id == user_id)
        .execution_options(populate_existing=True)
    )

    if preferences is None or not preferences.conversation_history:
        raise HTTPException(
            status_code=403,
            detail="Conversation history is disabled.",
        )


def get_conversation(
    db: Session,
    user_id: UUID,
    conversation_id: UUID,
) -> Conversation:

    conversation = db.scalar(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return conversation


def create_conversation(
    db: Session,
    user_id: UUID,
    title: str,
) -> Conversation:

    require_history_enabled(db, user_id)

    conversation = Conversation(
        user_id=user_id,
        title=title,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def list_conversations(
    db: Session,
    user_id: UUID,
    limit: int,
    offset: int,
):

    condition = Conversation.user_id == user_id

    total = db.scalar(
        select(func.count())
        .select_from(Conversation)
        .where(condition)
    )

    items = db.scalars(
        select(Conversation)
        .where(condition)
        .order_by(
            Conversation.updated_at.desc(),
            Conversation.id.desc(),
        )
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "items": items,
        "total": total or 0,
        "limit": limit,
        "offset": offset,
    }


def rename_conversation(
    db: Session,
    user_id: UUID,
    conversation_id: UUID,
    title: str,
):

    conversation = get_conversation(
        db, user_id, conversation_id
    )

    conversation.title = title
    conversation.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(conversation)

    return conversation


def delete_conversation(
    db: Session,
    user_id: UUID,
    conversation_id: UUID,
) -> None:

    conversation = get_conversation(
        db, user_id, conversation_id
    )

    db.delete(conversation)
    db.commit()


def clear_history(
    db: Session,
    user_id: UUID,
) -> None:

    db.execute(
        select(User.id)
        .where(User.id == user_id)
        .with_for_update()
    )

    db.execute(
        delete(Conversation).where(
            Conversation.user_id == user_id
        )
    )

    db.commit()


def add_message(
    db: Session,
    user_id: UUID,
    conversation_id: UUID,
    content: str,
    language: str | None = None,
    role: str = "user",
):

    require_history_enabled(db, user_id)

    conversation = db.scalar(
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        .with_for_update()
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    message = Message(
        conversation_id=conversation.id,
        role=role,
        content=content,
        language=language,
    )

    conversation.updated_at = datetime.now(timezone.utc)

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def list_messages(
    db: Session,
    user_id: UUID,
    conversation_id: UUID,
    limit: int,
    offset: int,
):

    get_conversation(db, user_id, conversation_id)

    condition = Message.conversation_id == conversation_id

    total = db.scalar(
        select(func.count())
        .select_from(Message)
        .where(condition)
    )

    items = db.scalars(
        select(Message)
        .where(condition)
        .order_by(
            Message.created_at.asc(),
            Message.id.asc(),
        )
        .offset(offset)
        .limit(limit)
    ).all()

    return {
        "items": items,
        "total": total or 0,
        "limit": limit,
        "offset": offset,
    }
