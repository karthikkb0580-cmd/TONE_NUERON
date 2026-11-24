from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from backend.app.database.session import get_db

from backend.app.models.user import User
from backend.app.models.refresh_token import RefreshToken

from backend.app.api.auth import (
    get_current_session,
    get_current_user,
)

from backend.app.schemas.session import (
    RefreshRequest,
    TokenPairResponse,
)

from backend.app.services.session_service import (
    refresh_session,
)

from backend.app.services.security_event_service import (
    log_security_event,
    SecurityEventType,
)
from fastapi import Request

from backend.app.services.session_service import (
    refresh_session,
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Sessions"],
)

@router.post(
    "/refresh",
    response_model=TokenPairResponse,
)
def refresh_token(
    request: Request,
    data: RefreshRequest,
    db: Session = Depends(get_db),
):

    ip_address = (
        request.client.host
        if request.client
        else None
    )

    return refresh_session(
        db,
        data.refresh_token,
        ip_address=ip_address,
    )

@router.post("/logout")
def logout(
    request: Request,
    session: RefreshToken = Depends(get_current_session),
    db: Session = Depends(get_db),
):
    ip_address = (
        request.client.host
        if request.client
        else None
    )

    session.is_revoked = True

    log_security_event(
        db=db,
        event_type=SecurityEventType.LOGOUT,
        user_id=session.user_id,
        ip_address=ip_address,
        details="Current session logged out",
    )

    db.commit()

    return {
        "message": "Logged out successfully."
    }

@router.post("/logout-all")
def logout_all(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ip_address = (
        request.client.host
        if request.client
        else None
    )

    db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.is_revoked.is_(False),
        )
        .values(is_revoked=True)
    )

    log_security_event(
        db=db,
        event_type=SecurityEventType.LOGOUT_ALL,
        user_id=current_user.id,
        ip_address=ip_address,
        details="All active sessions revoked",
    )

    db.commit()

    return {
        "message": (
            "Logged out from all sessions successfully."
        )
    }

@router.get("/sessions")
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    sessions = db.scalars(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == current_user.id,
            RefreshToken.is_revoked.is_(False),
            RefreshToken.expires_at > now,
        )
        .order_by(RefreshToken.created_at.desc())
    ).all()

    return {
        "sessions": [
            {
                "id": str(session.id),
                "created_at": session.created_at,
                "expires_at": session.expires_at,
                "is_revoked": session.is_revoked,
            }
            for session in sessions
        ]
    }