from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.schemas.otp import (
    SendOTPRequest,
    VerifyOTPRequest,
    OTPResponse,
)
from backend.app.services.otp_service import (
    create_email_otp,
    verify_email_otp,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Email Verification"],
)


@router.post(
    "/send-otp",
    response_model=OTPResponse,
)
def send_otp(
    data: SendOTPRequest,
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()

    user = db.scalar(
        select(User).where(
            func.lower(User.email) == email
        )
    )

    if user and user.is_active and not user.is_verified:
        create_email_otp(db, user)

    return OTPResponse(
        message=(
            "If email verification is required, "
            "a verification code will be sent."
        )
    )


@router.post(
    "/verify-email",
    response_model=OTPResponse,
)
def verify_email(
    data: VerifyOTPRequest,
    db: Session = Depends(get_db),
):
    email = str(data.email).strip().lower()

    user = db.scalar(
        select(User).where(
            func.lower(User.email) == email
        )
    )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP.",
        )

    if user.is_verified:
        return OTPResponse(
            message="Email is already verified."
        )

    verify_email_otp(
        db,
        user,
        data.otp,
    )

    return OTPResponse(
        message="Email verified successfully."
    )