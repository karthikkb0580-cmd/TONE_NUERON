from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.conversation import Conversation
from backend.app.models.feedback import Feedback
from backend.app.models.message import Message
from backend.app.schemas.feedback import FeedbackCreate
from backend.app.services.conversation_service import require_history_enabled


def save_feedback(
    db: Session,
    user_id: UUID,
    data: FeedbackCreate,
):
    try:
        require_history_enabled(db, user_id)

        message = db.scalar(
            select(Message)
            .join(
                Conversation,
                Conversation.id == Message.conversation_id,
            )
            .where(
                Message.id == data.message_id,
                Conversation.user_id == user_id,
                Message.role == "assistant",
            )
            .with_for_update(of=Message)
        )

        if message is None:
            raise HTTPException(
                status_code=404,
                detail="AI response not found.",
            )

        feedback = db.scalar(
            select(Feedback).where(
                Feedback.user_id == user_id,
                Feedback.message_id == data.message_id,
            )
        )

        if feedback is None:
            feedback = Feedback(
                user_id=user_id,
                message_id=data.message_id,
            )

            db.add(feedback)

        feedback.rating = data.rating
        feedback.reaction = data.reaction
        feedback.comment = data.comment

        db.commit()
        db.refresh(feedback)

        return feedback

    except Exception:
        db.rollback()
        raise


def list_feedback(
    db: Session,
    user_id: UUID,
    limit: int,
    offset: int,
):
    return db.scalars(
        select(Feedback)
        .where(Feedback.user_id == user_id)
        .order_by(
            Feedback.created_at.desc(),
            Feedback.id.desc(),
        )
        .offset(offset)
        .limit(limit)
    ).all()


def delete_feedback(
    db: Session,
    user_id: UUID,
    feedback_id: UUID,
):
    feedback = db.scalar(
        select(Feedback).where(
            Feedback.id == feedback_id,
            Feedback.user_id == user_id,
        )
    )

    if feedback is None:
        raise HTTPException(
            status_code=404,
            detail="Feedback not found.",
        )

    db.delete(feedback)
    db.commit()
