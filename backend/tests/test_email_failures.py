import pytest

from backend.app.core.exceptions import EmailDeliveryError
from backend.app.services import email_service, otp_service
from backend.app.models.user import User
from sqlalchemy import select


def test_email_provider_failure(monkeypatch):

    def fail(*args, **kwargs):
        raise RuntimeError("Provider unavailable")

    monkeypatch.setattr(
        email_service.resend.Emails,
        "send",
        fail,
    )

    with pytest.raises(EmailDeliveryError):
        email_service.send_email(
            "test@example.com",
            "Test",
            "Test body",
        )


def test_email_provider_missing_id(monkeypatch):

    monkeypatch.setattr(
        email_service.resend.Emails,
        "send",
        lambda *args, **kwargs: {},
    )

    with pytest.raises(EmailDeliveryError):
        email_service.send_email(
            "test@example.com",
            "Test",
            "Test body",
        )


def test_registration_email_failure(
    client,
    db_session,
    monkeypatch,
):

    def fail(*args, **kwargs):
        raise EmailDeliveryError()

    monkeypatch.setattr(
        otp_service,
        "send_verification_email",
        fail,
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "emailfailure@example.com",
            "username": "email_failure_test",
            "password": "TestPassword@123",
        },
    )

    assert response.status_code == 503

    user = db_session.scalar(
        select(User).where(
            User.email == "emailfailure@example.com"
        )
    )

    assert user is not None
    assert user.is_verified is False
