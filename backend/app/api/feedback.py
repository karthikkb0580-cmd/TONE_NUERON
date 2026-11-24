from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.feedback import (
    FeedbackCreate,
    FeedbackResponse,
)
from backend.app.services import feedback_service


router = APIRouter(
    prefix="/api/v1/feedback",
    tags=["AI Feedback"],
)


@router.post("", response_model=FeedbackResponse)
def submit_feedback(
    data: FeedbackCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return feedback_service.save_feedback(
        db, user.id, data
    )


@router.get("", response_model=list[FeedbackResponse])
def get_feedback(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return feedback_service.list_feedback(
        db, user.id, limit, offset
    )


@router.delete("/{feedback_id}", status_code=204)
def remove_feedback(
    feedback_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    feedback_service.delete_feedback(
        db, user.id, feedback_id
    )

    return Response(status_code=204)
