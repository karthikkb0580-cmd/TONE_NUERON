import re
import pytest

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select

from backend.app.models.user import User
from backend.app.models.email_otp import EmailOTP

from backend.app.services import otp_service

from backend.app.services.otp_service import (
    generate_otp,
    hash_otp,
    create_email_otp,
    verify_email_otp,
)

from backend.app.core.config import settings


def create_test_user(db, email="otp@example.com"):

    user = User(
        email=email,
        username=email.split("@")[0],
        password_hash="test-password-hash",
        is_active=True,
        is_verified=False,
    )

    db.add(user)
    db.flush()

    return user


def capture_email(monkeypatch):

    sent_emails = []

    def fake_send_verification_email(
        recipient_email,
        otp,
    ):
        sent_emails.append({
            "email": recipient_email,
            "otp": otp,
        })

    monkeypatch.setattr(
        otp_service,
        "send_verification_email",
        fake_send_verification_email,
    )

    return sent_emails


def get_otp_record(db, user):

    return db.scalar(
        select(EmailOTP).where(
            EmailOTP.user_id == user.id
        )
    )


def test_generate_six_digit_otp():

    otp = generate_otp()

    assert isinstance(otp, str)
    assert re.fullmatch(r"\d{6}", otp)


def test_hash_otp():

    otp = "123456"
    user_id = "test-user-id"

    first_hash = hash_otp(user_id, otp)
    second_hash = hash_otp(user_id, otp)

    assert first_hash == second_hash
    assert first_hash != otp


def test_create_email_otp(db_session, monkeypatch):

    sent_emails = capture_email(monkeypatch)

    user = create_test_user(db_session)

    create_email_otp(db_session, user)

    assert len(sent_emails) == 1

    assert sent_emails[0]["email"] == user.email

    otp = sent_emails[0]["otp"]

    assert re.fullmatch(r"\d{6}", otp)

    record = get_otp_record(db_session, user)

    assert record is not None
    assert record.attempts == 0
    assert record.otp_hash != otp
    assert record.expires_at > datetime.now(timezone.utc)


def test_verify_correct_otp(db_session, monkeypatch):

    sent_emails = capture_email(monkeypatch)

    user = create_test_user(db_session)

    create_email_otp(db_session, user)

    otp = sent_emails[0]["otp"]

    verify_email_otp(
        db_session,
        user,
        otp,
    )

    assert user.is_verified is True

    assert get_otp_record(db_session, user) is None


def test_verify_incorrect_otp(db_session, monkeypatch):

    capture_email(monkeypatch)

    user = create_test_user(db_session)

    create_email_otp(db_session, user)

    with pytest.raises(HTTPException) as exc:

        verify_email_otp(
            db_session,
            user,
            "000000",
        )

    assert exc.value.status_code == 400
    assert user.is_verified is False

    record = get_otp_record(db_session, user)

    assert record.attempts == 1


def test_expired_otp(db_session, monkeypatch):

    sent_emails = capture_email(monkeypatch)

    user = create_test_user(db_session)

    create_email_otp(db_session, user)

    record = get_otp_record(db_session, user)

    record.expires_at = (
        datetime.now(timezone.utc)
        - timedelta(minutes=5)
    )

    db_session.commit()

    with pytest.raises(HTTPException) as exc:

        verify_email_otp(
            db_session,
            user,
            sent_emails[0]["otp"],
        )

    assert exc.value.status_code == 400
    assert user.is_verified is False

    assert get_otp_record(db_session, user) is None


def test_maximum_otp_attempts(db_session, monkeypatch):

    capture_email(monkeypatch)

    user = create_test_user(db_session)

    create_email_otp(db_session, user)

    for _ in range(settings.OTP_MAX_ATTEMPTS):

        with pytest.raises(HTTPException) as exc:

            verify_email_otp(
                db_session,
                user,
                "000000",
            )

        assert exc.value.status_code == 400

    record = get_otp_record(db_session, user)

    assert record.attempts == settings.OTP_MAX_ATTEMPTS

    with pytest.raises(HTTPException) as exc:

        verify_email_otp(
            db_session,
            user,
            "000000",
        )

    assert exc.value.status_code == 429


def test_otp_resend_cooldown(db_session, monkeypatch):

    sent_emails = capture_email(monkeypatch)

    user = create_test_user(db_session)

    create_email_otp(db_session, user)

    assert len(sent_emails) == 1

    with pytest.raises(HTTPException) as exc:

        create_email_otp(
            db_session,
            user,
        )

    assert exc.value.status_code == 429
    assert len(sent_emails) == 1