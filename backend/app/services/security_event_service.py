import logging
import uuid

from sqlalchemy.orm import Session

from backend.app.models.user import User
from backend.app.models.security_event import SecurityEvent


logger = logging.getLogger(__name__)


class SecurityEventType:
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    ACCOUNT_BLOCKED = "ACCOUNT_BLOCKED"
    TOKEN_REUSE_DETECTED = "TOKEN_REUSE_DETECTED"
    SESSION_REVOKED = "SESSION_REVOKED"
    LOGOUT = "LOGOUT"
    LOGOUT_ALL = "LOGOUT_ALL"
    PASSWORD_RESET = "PASSWORD_RESET"


def log_security_event(
    db: Session,
    event_type: str,
    user_id: uuid.UUID | None = None,
    ip_address: str | None = None,
    details: str | None = None,
) -> SecurityEvent:

    event = SecurityEvent(
        user_id=user_id,
        event_type=event_type,
        ip_address=ip_address,
        details=details,
    )

    db.add(event)
    db.flush()

    logger.info(
        "Security event recorded: %s",
        event_type,
    )

    return event