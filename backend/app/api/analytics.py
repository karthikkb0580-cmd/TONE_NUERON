from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
)
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.analytics import AnalyticsSummary
from backend.app.services import analytics_service


router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Usage Analytics"],
)


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
)
def summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return analytics_service.get_summary(
        db, user.id, days
    )


@router.delete("", status_code=204)
def clear(
    confirm: bool = Query(False),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Confirmation is required.",
        )

    analytics_service.clear_analytics(
        db, user.id
    )

    return Response(status_code=204)
