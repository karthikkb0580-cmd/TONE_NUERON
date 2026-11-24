import pytest

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select

from backend.app.models.user import User
from backend.app.models.email_otp import EmailOTP

from backend.app.schemas.auth import LoginRequest

from backend.app.services import password_reset_service

from backend.app.services.password_reset_service import (
    generate_reset_otp,
    hash_reset_otp,
    create_password_reset_otp,
    reset_password,
    RESET_PURPOSE,
)

from backend.app.services.auth_service import (
    hash_password,
    authenticate_user,
)

from backend.app.core.config import settings


def create_test_user(db_session):

    user = User(
        email="reset@example.com",
        username="resetuser",
        password_hash=hash_password("OldPassword123!"),
        is_active=True,
        is_verified=True,
    )

    db_session.add(user)
    db_session.flush()

    return user


def prepare_reset(db_session, monkeypatch):

    sent_emails = []

    monkeypatch.setattr(
        password_reset_service,
        "generate_reset_otp",
        lambda: "123456",
    )

    monkeypatch.setattr(
        password_reset_service,
        "send_password_reset_email",
        lambda recipient_email, otp: sent_emails.append({
            "email": recipient_email,
            "otp": otp,
        }),
    )

    user = create_test_user(db_session)

    create_password_reset_otp(
        db_session,
        user,
    )

    return user, sent_emails


def test_generate_reset_otp():

    otp = generate_reset_otp()

    assert len(otp) == 6
    assert otp.isdigit()


def test_hash_reset_otp():

    first = hash_reset_otp("user-id", "123456")

    second = hash_reset_otp("user-id", "123456")

    assert first == second
    assert first != "123456"


def test_create_password_reset_otp(
    db_session,
    monkeypatch,
):

    user, sent_emails = prepare_reset(
        db_session,
        monkeypatch,
    )

    challenge = db_session.scalar(
        select(EmailOTP).where(
            EmailOTP.user_id == user.id,
            EmailOTP.purpose == RESET_PURPOSE,
        )
    )

    assert challenge is not None
    assert challenge.otp_hash != "123456"

    assert sent_emails[0]["email"] == user.email
    assert sent_emails[0]["otp"] == "123456"


def test_verify_correct_otp_and_reset_password(
    db_session,
    monkeypatch,
):

    user, sent_emails = prepare_reset(
        db_session,
        monkeypatch,
    )

    reset_password(
        db=db_session,
        user=user,
        otp=sent_emails[0]["otp"],
        new_password="NewPassword123!",
    )

    with pytest.raises(HTTPException) as exc:

        authenticate_user(
            db_session,
            user.email,
            "OldPassword123!",
        )

    assert exc.value.status_code == 401

    authenticated = authenticate_user(
        db_session,
        user.email,
        "NewPassword123!",
    )

    assert authenticated.id == user.id

    challenge = db_session.scalar(
        select(EmailOTP).where(
            EmailOTP.user_id == user.id,
            EmailOTP.purpose == RESET_PURPOSE,
        )
    )

    assert challenge is None


def test_verify_incorrect_reset_otp(
    db_session,
    monkeypatch,
):

    user, _ = prepare_reset(
        db_session,
        monkeypatch,
    )

    with pytest.raises(HTTPException) as exc:

        reset_password(
            db=db_session,
            user=user,
            otp="999999",
            new_password="NewPassword123!",
        )

    assert exc.value.status_code == 400

    challenge = db_session.scalar(
        select(EmailOTP).where(
            EmailOTP.user_id == user.id,
            EmailOTP.purpose == RESET_PURPOSE,
        )
    )

    assert challenge.attempts == 1


def test_expired_reset_otp(
    db_session,
    monkeypatch,
):

    user, _ = prepare_reset(
        db_session,
        monkeypatch,
    )

    challenge = db_session.scalar(
        select(EmailOTP).where(
            EmailOTP.user_id == user.id,
            EmailOTP.purpose == RESET_PURPOSE,
        )
    )

    challenge.expires_at = (
        datetime.now(timezone.utc) - timedelta(minutes=5)
    )

    db_session.commit()

    with pytest.raises(HTTPException) as exc:

        reset_password(
            db=db_session,
            user=user,
            otp="123456",
            new_password="NewPassword123!",
        )

    assert exc.value.status_code == 400


def test_maximum_reset_otp_attempts(
    db_session,
    monkeypatch,
):

    user, _ = prepare_reset(
        db_session,
        monkeypatch,
    )

    challenge = db_session.scalar(
        select(EmailOTP).where(
            EmailOTP.user_id == user.id,
            EmailOTP.purpose == RESET_PURPOSE,
        )
    )

    challenge.attempts = settings.OTP_MAX_ATTEMPTS

    db_session.commit()

    with pytest.raises(HTTPException) as exc:

        reset_password(
            db=db_session,
            user=user,
            otp="123456",
            new_password="NewPassword123!",
        )

    assert exc.value.status_code == 429


def test_reset_otp_resend_cooldown(
    db_session,
    monkeypatch,
):

    user, _ = prepare_reset(
        db_session,
        monkeypatch,
    )

    with pytest.raises(HTTPException) as exc:

        create_password_reset_otp(
            db_session,
            user,
        )

    assert exc.value.status_code == 429


def test_reset_otp_cannot_be_reused(
    db_session,
    monkeypatch,
):

    user, sent_emails = prepare_reset(
        db_session,
        monkeypatch,
    )

    reset_password(
        db=db_session,
        user=user,
        otp=sent_emails[0]["otp"],
        new_password="NewPassword123!",
    )

    with pytest.raises(HTTPException) as exc:

        reset_password(
            db=db_session,
            user=user,
            otp=sent_emails[0]["otp"],
            new_password="AnotherPassword123!",
        )

    assert exc.value.status_code == 400