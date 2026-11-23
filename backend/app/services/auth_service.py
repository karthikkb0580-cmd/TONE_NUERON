from datetime import datetime, timedelta, timezone

import jwt

from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.user import User
from backend.app.schemas.auth import RegisterRequest
from backend.app.services.otp_service import create_email_otp


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hasher.verify(
        plain_password,
        hashed_password,
    )


def register_user(
    db: Session,
    data: RegisterRequest,
) -> User:
    email = str(data.email).strip().lower()
    username = data.username.strip()

    existing_email = db.scalar(
        select(User).where(
            func.lower(User.email) == email
        )
    )

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="Email is already registered.",
        )

    existing_username = db.scalar(
        select(User).where(
            func.lower(User.username) == username.lower()
        )
    )

    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="Username is already taken.",
        )

    user = User(
        email=email,
        username=username,
        password_hash=hash_password(data.password),
        is_active=True,
        is_verified=False,
    )

    try:
        db.add(user)
        db.flush()

        # Commit the pending account so it remains
        # available for OTP resend if email delivery fails.
        db.commit()
        db.refresh(user)

    except Exception:
        db.rollback()
        raise

    # Automatically generate and send the OTP.
    create_email_otp(db, user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    user = db.scalar(
        select(User).where(
            func.lower(User.email) == email.strip().lower()
        )
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not verify_password(
        password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is disabled.",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in.",
        )

    return user


def create_access_token(user_id) -> str:
    expires_at = datetime.now(
        timezone.utc
    ) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )