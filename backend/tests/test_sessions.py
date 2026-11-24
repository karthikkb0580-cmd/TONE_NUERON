import uuid

import pytest

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import select

from backend.app.models.user import User
from backend.app.models.refresh_token import RefreshToken
from backend.app.models.used_refresh_token import UsedRefreshToken

from backend.app.services.session_service import (
    create_session,
    refresh_session,
    revoke_session,
    revoke_all_sessions,
)


def create_test_user(db):

    user = User(
        email=f"{uuid.uuid4().hex[:10]}@example.com",
        username=f"user_{uuid.uuid4().hex[:10]}",
        password_hash="test-password-hash",
        is_active=True,
        is_verified=True,
    )

    db.add(user)
    db.flush()

    return user


def get_session(db, user):

    return db.scalar(
        select(RefreshToken).where(
            RefreshToken.user_id == user.id
        ).order_by(RefreshToken.expires_at.desc())
    )


def test_create_session(db_session):

    user = create_test_user(db_session)

    tokens = create_session(
        db_session,
        user.id,
    )

    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"

    session = get_session(db_session, user)

    assert session is not None
    assert session.user_id == user.id
    assert session.is_revoked is False


def test_refresh_token_rotation(db_session):

    user = create_test_user(db_session)

    original = create_session(
        db_session,
        user.id,
    )

    refreshed = refresh_session(
        db_session,
        original["refresh_token"],
    )

    assert refreshed["access_token"]
    assert refreshed["refresh_token"]

    assert (
        refreshed["refresh_token"]
        != original["refresh_token"]
    )

    session = get_session(db_session, user)

    assert session is not None
    assert session.is_revoked is False

    used_token = db_session.scalar(
        select(UsedRefreshToken).where(
            UsedRefreshToken.session_id == session.id
        )
    )

    assert used_token is not None


def test_old_refresh_token_rejected(db_session):

    user = create_test_user(db_session)

    original = create_session(
        db_session,
        user.id,
    )

    refresh_session(
        db_session,
        original["refresh_token"],
    )

    with pytest.raises(HTTPException) as exc:

        refresh_session(
            db_session,
            original["refresh_token"],
        )

    assert exc.value.status_code == 401


def test_refresh_token_reuse_revokes_session(db_session):

    user = create_test_user(db_session)

    original = create_session(
        db_session,
        user.id,
    )

    refresh_session(
        db_session,
        original["refresh_token"],
    )

    session = get_session(db_session, user)

    assert session.is_revoked is False

    with pytest.raises(HTTPException) as exc:

        refresh_session(
            db_session,
            original["refresh_token"],
        )

    assert exc.value.status_code == 401

    db_session.refresh(session)

    assert session.is_revoked is True


def test_invalid_refresh_token(db_session):

    with pytest.raises(HTTPException) as exc:

        refresh_session(
            db_session,
            "invalid-refresh-token",
        )

    assert exc.value.status_code == 401


def test_expired_refresh_token(db_session):

    user = create_test_user(db_session)

    tokens = create_session(
        db_session,
        user.id,
    )

    session = get_session(db_session, user)

    session.expires_at = (
        datetime.now(timezone.utc)
        - timedelta(minutes=5)
    )

    db_session.commit()

    with pytest.raises(HTTPException) as exc:

        refresh_session(
            db_session,
            tokens["refresh_token"],
        )

    assert exc.value.status_code == 401


def test_revoke_single_session(db_session):

    user = create_test_user(db_session)

    tokens = create_session(
        db_session,
        user.id,
    )

    session = get_session(db_session, user)

    revoke_session(
        db_session,
        session.id,
        user.id,
    )

    db_session.refresh(session)

    assert session.is_revoked is True


def test_revoke_all_sessions(db_session):

    user = create_test_user(db_session)

    create_session(db_session, user.id)
    create_session(db_session, user.id)

    revoke_all_sessions(
        db_session,
        user.id,
    )

    sessions = db_session.scalars(
        select(RefreshToken).where(
            RefreshToken.user_id == user.id
        )
    ).all()

    assert len(sessions) == 2

    assert all(
        session.is_revoked
        for session in sessions
    )
