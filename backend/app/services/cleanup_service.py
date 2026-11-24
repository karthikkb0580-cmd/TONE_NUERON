from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlalchemy.orm import Session

from backend.app.models.email_otp import EmailOTP
from backend.app.models.refresh_token import RefreshToken
from backend.app.models.security_event import SecurityEvent
from backend.app.models.usage import UsageEvent

from backend.app.core.retention_config import retention_settings
from backend.app.schemas.privacy import CleanupResponse


def cleanup_database(db: Session):

    now = datetime.now(timezone.utc)

    analytics_cutoff = now - timedelta(
        days=retention_settings.ANALYTICS_RETENTION_DAYS
    )

    security_cutoff = now - timedelta(
        days=retention_settings.SECURITY_EVENT_RETENTION_DAYS
    )

    try:

        expired_otps = db.execute(
            delete(EmailOTP).where(
                EmailOTP.expires_at <= now
            )
        ).rowcount

        expired_sessions = db.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at <= now
            )
        ).rowcount

        old_analytics = db.execute(
            delete(UsageEvent).where(
                UsageEvent.created_at < analytics_cutoff
            )
        ).rowcount

        old_security_events = db.execute(
            delete(SecurityEvent).where(
                SecurityEvent.created_at < security_cutoff
            )
        ).rowcount

        db.commit()

        return CleanupResponse(
            expired_otps=expired_otps,
            expired_sessions=expired_sessions,
            old_analytics_events=old_analytics,
            old_security_events=old_security_events,
        )

    except Exception:
        db.rollback()
        raise
