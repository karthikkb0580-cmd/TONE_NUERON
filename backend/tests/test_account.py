import pytest

from fastapi import HTTPException
from sqlalchemy import select

from backend.app.models.user import User
from backend.app.services.auth_service import (
    hash_password,
    verify_password,
)
from backend.app.services.account_service import (
    change_password,
    delete_account,
)
from backend.app.services.session_service import create_session
from backend.app.models.refresh_token import RefreshToken


@pytest.fixture
def account_user(db_session):
    user = User(
        email="account@example.com",
        username="account_test",
        password_hash=hash_password("OldPassword123"),
        is_verified=True,
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()

    return user


def test_change_password(db_session, account_user):
    create_session(db_session, account_user.id)

    change_password(
        db_session,
        account_user,
        "OldPassword123",
        "NewPassword123",
    )

    assert verify_password(
        "NewPassword123",
        account_user.password_hash,
    )

    sessions = db_session.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == account_user.id
        )
    ).all()

    assert sessions
    assert all(session.is_revoked for session in sessions)


def test_incorrect_current_password(db_session, account_user):
    with pytest.raises(HTTPException) as exc:
        change_password(
            db_session,
            account_user,
            "WrongPassword",
            "NewPassword123",
        )

    assert exc.value.status_code == 400


def test_same_password_rejected(db_session, account_user):
    with pytest.raises(HTTPException) as exc:
        change_password(
            db_session,
            account_user,
            "OldPassword123",
            "OldPassword123",
        )

    assert exc.value.status_code == 400


def test_delete_account(db_session, account_user):
    user_id = account_user.id

    delete_account(
        db_session,
        account_user,
        "OldPassword123",
        "DELETE",
    )

    assert db_session.get(User, user_id) is None


def test_delete_wrong_password(db_session, account_user):
    with pytest.raises(HTTPException) as exc:
        delete_account(
            db_session,
            account_user,
            "WrongPassword",
            "DELETE",
        )

    assert exc.value.status_code == 400


def test_delete_without_confirmation(db_session, account_user):
    with pytest.raises(HTTPException) as exc:
        delete_account(
            db_session,
            account_user,
            "OldPassword123",
            "NO",
        )

    assert exc.value.status_code == 400
