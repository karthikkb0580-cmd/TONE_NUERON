import hashlib
import secrets
import uuid

from datetime import datetime, timedelta, timezone

import jwt

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.app.core.config import settings

from backend.app.models.refresh_token import RefreshToken
from backend.app.models.used_refresh_token import UsedRefreshToken

from backend.app.services.security_event_service import (
    log_security_event,
    SecurityEventType,
)

ACCESS_TOKEN_MINUTES = 15
REFRESH_TOKEN_DAYS = 7

def utc_now():
    return datetime.now(timezone.utc)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_access_token(
    user_id: uuid.UUID,
    session_id: uuid.UUID,
) -> str:

    payload = {
        "sub": str(user_id),
        "sid": str(session_id),
        "type": "access",
        "iat": utc_now(),
        "exp": utc_now() + timedelta(
            minutes=ACCESS_TOKEN_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

def create_session(
    db: Session,
    user_id: uuid.UUID,
) -> dict:

    refresh_token = secrets.token_urlsafe(48)

    session = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(refresh_token),
        expires_at=utc_now() + timedelta(
            days=REFRESH_TOKEN_DAYS
        ),
        is_revoked=False,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    access_token = create_access_token(
        user_id,
        session.id,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

def refresh_session(
    db: Session,
    refresh_token: str,
    ip_address: str | None = None,
) -> dict:

    token_hash = hash_token(refresh_token)

    session = db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .with_for_update()
    )

    if session is None:

        used_token = db.scalar(
            select(UsedRefreshToken)
            .where(
                UsedRefreshToken.token_hash == token_hash
            )
        )

        if used_token is not None:

            try:
                affected_session = db.scalar(
                    select(RefreshToken)
                    .where(
                        RefreshToken.id == used_token.session_id
                    )
                    .with_for_update()
                )

                if affected_session is not None:

                    affected_session.is_revoked = True

                    log_security_event(
                        db=db,
                        event_type=SecurityEventType.TOKEN_REUSE_DETECTED,
                        user_id=affected_session.user_id,
                        ip_address=ip_address,
                        details=(
                            "Previously used refresh token reused. "
                            "Affected session revoked."
                        ),
                    )

                    log_security_event(
                        db=db,
                        event_type=SecurityEventType.SESSION_REVOKED,
                        user_id=affected_session.user_id,
                        ip_address=ip_address,
                        details=(
                            "Session revoked following "
                            "refresh token reuse detection."
                        ),
                    )

                else:

                    log_security_event(
                        db=db,
                        event_type=SecurityEventType.TOKEN_REUSE_DETECTED,
                        ip_address=ip_address,
                        details=(
                            "Previously used refresh token detected."
                        ),
                    )

                db.commit()

            except Exception:
                db.rollback()
                raise

            raise HTTPException(
                status_code=401,
                detail=(
                    "Refresh token reuse detected. "
                    "Session revoked."
                ),
            )

        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
        )

    if session.is_revoked:

        db.rollback()

        raise HTTPException(
            status_code=401,
            detail="Session has been revoked.",
        )
    if utc_now() >= session.expires_at:

        db.rollback()

        raise HTTPException(
            status_code=401,
            detail="Refresh token expired.",
        )
    try:

        used_token = UsedRefreshToken(
            session_id=session.id,
            token_hash=session.token_hash,
        )

        db.add(used_token)

        new_refresh_token = secrets.token_urlsafe(48)

        session.token_hash = hash_token(
            new_refresh_token
        )

        session.expires_at = utc_now() + timedelta(
            days=REFRESH_TOKEN_DAYS
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    access_token = create_access_token(
        session.user_id,
        session.id,
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }

def revoke_session(
    db: Session,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:

    session = db.scalar(
        select(RefreshToken).where(
            RefreshToken.id == session_id,
            RefreshToken.user_id == user_id,
        )
    )

    if session:
        session.is_revoked = True
        db.commit()


def revoke_all_sessions(
    db: Session,
    user_id: uuid.UUID,
) -> None:

    db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == user_id
        )
        .values(is_revoked=True)
    )

    db.commit()