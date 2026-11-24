from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.user_preference import UserPreference
from backend.app.schemas.preferences import (
    PreferencesUpdate,
    PreferencesResponse,
)


def get_preferences(
    db: Session,
    user: User,
):
    preferences = db.scalar(
        select(UserPreference).where(
            UserPreference.user_id == user.id
        )
    )

    if preferences is None:
        return PreferencesResponse()

    return preferences


def update_preferences(
    db: Session,
    user: User,
    data: PreferencesUpdate,
):
    try:
        db.execute(
            select(User.id)
            .where(User.id == user.id)
            .with_for_update()
        )

        preferences = db.scalar(
            select(UserPreference).where(
                UserPreference.user_id == user.id
            )
        )

        if preferences is None:
            preferences = UserPreference(
                user_id=user.id
            )
            db.add(preferences)

        for field, value in data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        ).items():
            setattr(preferences, field, value)

        db.commit()
        db.refresh(preferences)

        return preferences

    except Exception:
        db.rollback()
        raise
