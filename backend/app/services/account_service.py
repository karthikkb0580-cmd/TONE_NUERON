from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.refresh_token import RefreshToken
from backend.app.services.auth_service import (
    hash_password,
    verify_password,
)


def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
) -> None:

    try:
        locked_user = db.scalar(
            select(User)
            .where(User.id == user.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

        if locked_user is None or not locked_user.is_active:
            raise HTTPException(
                status_code=401,
                detail="Account unavailable.",
            )

        if not verify_password(
            current_password,
            locked_user.password_hash,
        ):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect.",
            )

        if verify_password(
            new_password,
            locked_user.password_hash,
        ):
            raise HTTPException(
                status_code=400,
                detail="New password must be different.",
            )

        locked_user.password_hash = hash_password(new_password)

        db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == locked_user.id)
            .values(is_revoked=True)
        )

        db.commit()

    except Exception:
        db.rollback()
        raise


def delete_account(
    db: Session,
    user: User,
    password: str,
    confirmation: str,
) -> None:

    try:
        if confirmation != "DELETE":
            raise HTTPException(
                status_code=400,
                detail="Type DELETE to confirm account deletion.",
            )

        locked_user = db.scalar(
            select(User)
            .where(User.id == user.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

        if locked_user is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found.",
            )

        if not verify_password(
            password,
            locked_user.password_hash,
        ):
            raise HTTPException(
                status_code=400,
                detail="Incorrect password.",
            )

        db.delete(locked_user)
        db.commit()

    except Exception:
        db.rollback()
        raise
