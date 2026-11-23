from backend.app.database.session import SessionLocal

from backend.app.services.security_event_service import (
    log_security_event,
    SecurityEventType,
)


def main():
    db = SessionLocal()

    try:
        event = log_security_event(
            db=db,
            event_type=SecurityEventType.LOGIN_FAILED,
            user_id=None,
            ip_address="127.0.0.1",
            details="Manual security logging test",
        )

        db.commit()

        print("Security event created successfully.")
        print("Event ID:", event.id)
        print("Event type:", event.event_type)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()