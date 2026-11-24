import pytest

from backend.app.models.user import User
from backend.app.services.auth_service import hash_password
from backend.app.services import password_reset_service


@pytest.fixture
def reset_user(db_session):

    user = User(
        email="apireset@example.com",
        username="apireset",
        password_hash=hash_password("OldPassword123!"),
        is_active=True,
        is_verified=True,
    )

    db_session.add(user)
    db_session.flush()

    return user


@pytest.fixture
def reset_email_mock(monkeypatch):

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

    return sent_emails


def test_forgot_password_success(
    client,
    reset_user,
    reset_email_mock,
):

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={
            "email": reset_user.email,
        },
    )

    assert response.status_code == 200

    assert len(reset_email_mock) == 1

    assert reset_email_mock[0]["email"] == reset_user.email


def test_forgot_password_unknown_email(client):

    response = client.post(
        "/api/v1/auth/forgot-password",
        json={
            "email": "unknown@example.com",
        },
    )

    assert response.status_code == 200

    assert "If the account is eligible" in response.json()["message"]


def test_reset_password_success(
    client,
    reset_user,
    reset_email_mock,
):

    client.post(
        "/api/v1/auth/forgot-password",
        json={
            "email": reset_user.email,
        },
    )

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": reset_user.email,
            "otp": "123456",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 200

    assert response.json()["message"] == "Password reset successfully."


def test_reset_password_invalid_otp(
    client,
    reset_user,
    reset_email_mock,
):

    client.post(
        "/api/v1/auth/forgot-password",
        json={
            "email": reset_user.email,
        },
    )

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": reset_user.email,
            "otp": "999999",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 400


def test_reset_password_unknown_email(client):

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": "unknown@example.com",
            "otp": "123456",
            "new_password": "NewPassword123!",
        },
    )

    assert response.status_code == 400


def test_reset_password_invalid_request(client):

    response = client.post(
        "/api/v1/auth/reset-password",
        json={
            "email": "invalid-email",
            "otp": "123",
            "new_password": "123",
        },
    )

    assert response.status_code == 422