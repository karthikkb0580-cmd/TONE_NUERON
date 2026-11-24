import pytest

from fastapi import HTTPException

from backend.app.models.user import User
from backend.app.schemas.auth import RegisterRequest

from backend.app.services import auth_service

from backend.app.services.auth_service import (
    register_user,
    authenticate_user,
    hash_password,
)


def create_register_data(
    email="newuser@example.com",
    username="newuser",
    password="StrongPassword123!",
):
    return RegisterRequest(
        email=email,
        username=username,
        password=password,
    )


def test_register_new_user(db_session, monkeypatch):

    otp_calls = []

    def fake_create_email_otp(db, user):
        otp_calls.append(user.email)

    monkeypatch.setattr(
        auth_service,
        "create_email_otp",
        fake_create_email_otp,
    )

    data = create_register_data()

    user = register_user(db_session, data)

    assert user.email == "newuser@example.com"
    assert user.username == "newuser"
    assert user.is_active is True
    assert user.is_verified is False

    assert user.password_hash != data.password

    assert otp_calls == ["newuser@example.com"]


def test_register_duplicate_email(db_session, monkeypatch):

    monkeypatch.setattr(
        auth_service,
        "create_email_otp",
        lambda db, user: None,
    )

    register_user(
        db_session,
        create_register_data(),
    )

    duplicate = create_register_data(
        email="newuser@example.com",
        username="differentuser",
    )

    with pytest.raises(HTTPException) as exc:

        register_user(
            db_session,
            duplicate,
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == "Email is already registered."


def test_register_duplicate_username(db_session, monkeypatch):

    monkeypatch.setattr(
        auth_service,
        "create_email_otp",
        lambda db, user: None,
    )

    register_user(
        db_session,
        create_register_data(),
    )

    duplicate = create_register_data(
        email="another@example.com",
        username="newuser",
    )

    with pytest.raises(HTTPException) as exc:

        register_user(
            db_session,
            duplicate,
        )

    assert exc.value.status_code == 409
    assert exc.value.detail == "Username is already taken."


def test_login_success(db_session):

    user = User(
        email="login@example.com",
        username="loginuser",
        password_hash=hash_password("StrongPassword123!"),
        is_active=True,
        is_verified=True,
    )

    db_session.add(user)
    db_session.flush()

    authenticated_user = authenticate_user(
        db_session,
        "login@example.com",
        "StrongPassword123!",
    )

    assert authenticated_user.id == user.id
    assert authenticated_user.email == "login@example.com"


def test_login_wrong_password(db_session):

    user = User(
        email="wrongpass@example.com",
        username="wrongpass",
        password_hash=hash_password("CorrectPassword123!"),
        is_active=True,
        is_verified=True,
    )

    db_session.add(user)
    db_session.flush()

    with pytest.raises(HTTPException) as exc:

        authenticate_user(
            db_session,
            "wrongpass@example.com",
            "IncorrectPassword123!",
        )

    assert exc.value.status_code == 401


def test_login_nonexistent_user(db_session):

    with pytest.raises(HTTPException) as exc:

        authenticate_user(
            db_session,
            "unknown@example.com",
            "SomePassword123!",
        )

    assert exc.value.status_code == 401


def test_login_unverified_user(db_session):

    user = User(
        email="unverified@example.com",
        username="unverified",
        password_hash=hash_password("StrongPassword123!"),
        is_active=True,
        is_verified=False,
    )

    db_session.add(user)
    db_session.flush()

    with pytest.raises(HTTPException) as exc:

        authenticate_user(
            db_session,
            "unverified@example.com",
            "StrongPassword123!",
        )

    assert exc.value.status_code == 403


def test_login_disabled_user(db_session):

    user = User(
        email="disabled@example.com",
        username="disabled",
        password_hash=hash_password("StrongPassword123!"),
        is_active=False,
        is_verified=True,
    )

    db_session.add(user)
    db_session.flush()

    with pytest.raises(HTTPException) as exc:

        authenticate_user(
            db_session,
            "disabled@example.com",
            "StrongPassword123!",
        )

    assert exc.value.status_code == 403