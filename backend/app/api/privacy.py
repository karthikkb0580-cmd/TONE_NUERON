from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.core.rate_limit import limiter
from backend.app.models.user import User

from backend.app.schemas.privacy import PrivacySummary
from backend.app.services.privacy_service import get_privacy_summary
from backend.app.services.export_service import export_user_data


router = APIRouter(
    prefix="/api/v1/privacy",
    tags=["Privacy"],
)


@router.get(
    "/summary",
    response_model=PrivacySummary,
)
def privacy_summary(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    return get_privacy_summary(db, user.id)


@router.get("/export")
@limiter.limit("3/hour")
def download_user_data(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):

    data = export_user_data(db, user.id)

    date = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    return JSONResponse(
        content=data,
        headers={
            "Content-Disposition": (
                f'attachment; filename="tone-neuron-data-{date}.json"'
            ),
            "Cache-Control": "no-store",
        },
    )
