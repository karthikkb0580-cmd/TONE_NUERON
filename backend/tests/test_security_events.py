from sqlalchemy import select

from backend.app.models.security_event import SecurityEvent
from backend.app.services.security_event_service import (
    log_security_event,
    SecurityEventType,
)


def test_log_login_success(db_session):
    event = log_security_event(
        db=db_session,
        event_type=SecurityEventType.LOGIN_SUCCESS,
        ip_address="127.0.0.1",
        details="Successful login",
    )

    db_session.commit()

    saved = db_session.get(SecurityEvent, event.id)

    assert saved is not None
    assert saved.event_type == "LOGIN_SUCCESS"
    assert saved.ip_address == "127.0.0.1"


def test_log_failed_login(db_session):
    event = log_security_event(
        db=db_session,
        event_type=SecurityEventType.LOGIN_FAILED,
        ip_address="127.0.0.1",
        details="Invalid credentials",
    )

    db_session.commit()

    saved = db_session.get(SecurityEvent, event.id)

    assert saved is not None
    assert saved.event_type == "LOGIN_FAILED"


def test_log_account_blocked(db_session):
    event = log_security_event(
        db=db_session,
        event_type=SecurityEventType.ACCOUNT_BLOCKED,
        details="Account blocked",
    )

    db_session.commit()

    saved = db_session.get(SecurityEvent, event.id)

    assert saved is not None
    assert saved.user_id is None
    assert saved.event_type == "ACCOUNT_BLOCKED"


def test_security_event_details(db_session):
    event = log_security_event(
        db=db_session,
        event_type=SecurityEventType.TOKEN_REUSE_DETECTED,
        details="Refresh token reuse detected",
    )

    db_session.commit()

    saved = db_session.get(SecurityEvent, event.id)

    assert saved.details == "Refresh token reuse detected"
