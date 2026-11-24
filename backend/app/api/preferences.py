from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_user
from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.preferences import (
    PreferencesResponse,
    PreferencesUpdate,
)
from backend.app.services.preferences_service import (
    get_preferences,
    update_preferences,
)

router = APIRouter(
    prefix="/api/v1/preferences",
    tags=["Preferences"],
)


@router.get("", response_model=PreferencesResponse)
def read_preferences(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return get_preferences(db, user)


@router.patch("", response_model=PreferencesResponse)
def edit_preferences(
    data: PreferencesUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return update_preferences(db, user, data)
