from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.user_profile import UserProfile
from backend.app.schemas.profile import ProfileUpdate


def get_profile(db: Session, user: User) -> UserProfile:
    profile = db.get(UserProfile, user.id)

    if profile is None:
        return UserProfile(
            user_id=user.id,
            display_name=user.username,
        )

    return profile


def update_profile(
    db: Session,
    user: User,
    data: ProfileUpdate,
) -> UserProfile:

    try:
        db.execute(
            select(User.id)
            .where(User.id == user.id)
            .with_for_update()
        )

        profile = db.get(UserProfile, user.id)

        if profile is None:
            profile = UserProfile(
                user_id=user.id,
                display_name=user.username,
            )
            db.add(profile)

        for field, value in data.model_dump(
            exclude_unset=True
        ).items():
            setattr(profile, field, value)

        db.commit()
        db.refresh(profile)

        return profile

    except Exception:
        db.rollback()
        raise
