from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User

from backend.app.schemas.password_reset import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    PasswordResetResponse,
)

from backend.app.services.password_reset_service import (
    create_password_reset_otp,
    reset_password,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Password Recovery"],
)


@router.post(
    "/forgot-password",
    response_model=PasswordResetResponse,
)
def forgot_password(
    data: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()

    user = db.scalar(
        select(User).where(
            func.lower(User.email) == email
        )
    )

    if user and user.is_active and user.is_verified:
        create_password_reset_otp(db, user)

    return PasswordResetResponse(
        message=(
            "If the account is eligible, "
            "a password reset code will be sent."
        )
    )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
)
def reset_user_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()

    user = db.scalar(
        select(User).where(
            func.lower(User.email) == email
        )
    )

    if not user or not user.is_active or not user.is_verified:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset code.",
        )

    reset_password(
        db=db,
        user=user,
        otp=data.otp,
        new_password=data.new_password,
    )

    return PasswordResetResponse(
        message="Password reset successfully."
    )