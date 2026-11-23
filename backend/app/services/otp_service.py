import hashlib
import hmac
import secrets

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.models.email_otp import EmailOTP
from backend.app.models.user import User
from backend.app.services.email_service import (
    send_verification_email,
)


OTP_PURPOSE = "email_verification"


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(user_id, otp: str) -> str:
    message = (
        f"{user_id}:{OTP_PURPOSE}:{otp}"
    ).encode("utf-8")

    return hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"),
        message,
        hashlib.sha256,
    ).hexdigest()


def create_email_otp(
    db: Session,
    user: User,
) -> None:
    # Lock the user row to serialize OTP requests.
    db.execute(
        select(User.id)
        .where(User.id == user.id)
        .with_for_update()
    ).first()

    now = datetime.now(timezone.utc)

    existing = db.scalar(
        select(EmailOTP).where(
            EmailOTP.user_id == user.id,
            EmailOTP.purpose == OTP_PURPOSE,
        )
    )

    if existing:
        elapsed = (
            now - existing.created_at
        ).total_seconds()

        if elapsed < settings.OTP_RESEND_COOLDOWN_SECONDS:
            db.rollback()

            raise HTTPException(
                status_code=429,
                detail=(
                    "Please wait before requesting "
                    "another verification code."
                ),
            )

        db.delete(existing)
        db.flush()

    otp = generate_otp()

    challenge = EmailOTP(
        user_id=user.id,
        purpose=OTP_PURPOSE,
        otp_hash=hash_otp(user.id, otp),
        expires_at=now + timedelta(
            minutes=settings.OTP_EXPIRE_MINUTES
        ),
        attempts=0,
        created_at=now,
    )

    db.add(challenge)

    try:
        db.flush()
        send_verification_email(
            recipient_email=user.email,
            otp=otp,
        )
        db.commit()

    except Exception:
        db.rollback()
        raise


def verify_email_otp(
    db: Session,
    user: User,
    otp: str,
) -> None:
    db.execute(
        select(User.id)
        .where(User.id == user.id)
        .with_for_update()
    ).first()

    challenge = db.scalar(
        select(EmailOTP)
        .where(
            EmailOTP.user_id == user.id,
            EmailOTP.purpose == OTP_PURPOSE,
        )
        .with_for_update()
    )

    if challenge is None:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP.",
        )

    now = datetime.now(timezone.utc)

    if now >= challenge.expires_at:
        db.delete(challenge)
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP.",
        )

    if challenge.attempts >= settings.OTP_MAX_ATTEMPTS:
        db.rollback()

        raise HTTPException(
            status_code=429,
            detail="Too many incorrect OTP attempts.",
        )

    expected_hash = hash_otp(
        user.id,
        otp,
    )

    if not hmac.compare_digest(
        expected_hash,
        challenge.otp_hash,
    ):
        challenge.attempts += 1
        db.commit()

        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP.",
        )

    user.is_verified = True

    db.delete(challenge)
    db.commit()