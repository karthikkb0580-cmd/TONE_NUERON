from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.profile import (
    ProfileResponse,
    ProfileUpdate,
)
from backend.app.services.profile_service import (
    get_profile,
    update_profile,
)

router = APIRouter(
    prefix="/api/v1/profile",
    tags=["Profile"],
)


@router.get("", response_model=ProfileResponse)
def read_profile(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_profile(db, user)


@router.patch("", response_model=ProfileResponse)
def edit_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return update_profile(db, user, data)
