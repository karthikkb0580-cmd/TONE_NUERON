import uuid

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.main import app
from backend.app.api.auth import get_current_user

from backend.app.models.user import User, UserPreferences
from backend.app.models.conversation import Conversation
from backend.app.models.message import Message
from backend.app.models.usage import UsageEvent

from backend.app.services.auth_service import hash_password
from backend.app.services.export_service import export_user_data
from backend.app.services.privacy_service import get_privacy_summary
from backend.app.services.cleanup_service import cleanup_database

from backend.app.core.retention_config import retention_settings


@pytest.fixture
def privacy_user(db_session):

    suffix = uuid.uuid4().hex[:12]

    user = User(
        email=f"privacy_{suffix}@example.com",
        username=f"privacy_{suffix}",
        password_hash=hash_password("TestPassword123!"),
        is_verified=True,
        is_active=True,
    )

    db_session.add(user)
    db_session.flush()

    db_session.add(
        UserPreferences(
            user_id=user.id,
            conversation_history=True,
            analytics_enabled=True,
        )
    )

    db_session.commit()
    db_session.refresh(user)

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        yield user

    finally:
        app.dependency_overrides.pop(
            get_current_user,
            None,
        )


def test_privacy_summary(client, privacy_user):

    response = client.get("/api/v1/privacy/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["conversation_history_enabled"] is True
    assert data["analytics_enabled"] is True
    assert data["total_conversations"] == 0
    assert data["total_messages"] == 0


def test_privacy_summary_counts(db_session, privacy_user):

    conversation = Conversation(
        user_id=privacy_user.id,
        title="Privacy test",
    )

    db_session.add(conversation)
    db_session.flush()

    db_session.add(
        Message(
            conversation_id=conversation.id,
            role="user",
            content="Test message",
        )
    )

    db_session.commit()

    result = get_privacy_summary(
        db_session,
        privacy_user.id,
    )

    assert result.total_conversations == 1
    assert result.total_messages == 1


def test_export_account(db_session, privacy_user):

    data = export_user_data(
        db_session,
        privacy_user.id,
    )

    assert data["account"]["email"] == privacy_user.email
    assert data["account"]["username"] == privacy_user.username


def test_export_excludes_secrets(db_session, privacy_user):

    data = export_user_data(
        db_session,
        privacy_user.id,
    )

    assert "password_hash" not in data["account"]
    assert "refresh_tokens" not in data
    assert "email_otps" not in data
    assert "used_refresh_tokens" not in data


def test_export_conversation(db_session, privacy_user):

    conversation = Conversation(
        user_id=privacy_user.id,
        title="Export test",
    )

    db_session.add(conversation)
    db_session.flush()

    db_session.add(
        Message(
            conversation_id=conversation.id,
            role="user",
            content="Export this message",
        )
    )

    db_session.commit()

    data = export_user_data(
        db_session,
        privacy_user.id,
    )

    assert len(data["conversations"]) == 1
    assert len(data["messages"]) == 1
    assert data["messages"][0]["content"] == "Export this message"


def test_export_isolation(db_session, privacy_user):

    suffix = uuid.uuid4().hex[:12]

    other_user = User(
        email=f"other_{suffix}@example.com",
        username=f"other_{suffix}",
        password_hash=hash_password("TestPassword123!"),
        is_verified=True,
        is_active=True,
    )

    db_session.add(other_user)
    db_session.flush()

    db_session.add(
        Conversation(
            user_id=other_user.id,
            title="Private conversation",
        )
    )

    db_session.commit()

    data = export_user_data(
        db_session,
        privacy_user.id,
    )

    assert data["conversations"] == []


def test_export_download(client, privacy_user):

    response = client.get("/api/v1/privacy/export")

    assert response.status_code == 200

    assert "attachment" in response.headers[
        "Content-Disposition"
    ]

    assert response.headers["Cache-Control"] == "no-store"


def test_privacy_authentication(client):

    response = client.get("/api/v1/privacy/summary")

    assert response.status_code in (401, 403)


def test_export_authentication(client):

    response = client.get("/api/v1/privacy/export")

    assert response.status_code in (401, 403)


def test_cleanup_old_analytics(db_session, privacy_user):

    event = UsageEvent(
        user_id=privacy_user.id,
        feature="rewrite",
        successful=True,
        processing_time_ms=100,
        created_at=datetime.now(timezone.utc) - timedelta(
            days=retention_settings.ANALYTICS_RETENTION_DAYS + 10
        ),
    )

    db_session.add(event)
    db_session.flush()

    event_id = event.id

    db_session.commit()

    result = cleanup_database(db_session)

    assert result.old_analytics_events == 1

    db_session.expire_all()

    assert db_session.get(UsageEvent, event_id) is None


def test_cleanup_preserves_recent_analytics(
    db_session,
    privacy_user,
):

    event = UsageEvent(
        user_id=privacy_user.id,
        feature="rewrite",
        successful=True,
        processing_time_ms=100,
    )

    db_session.add(event)
    db_session.flush()

    event_id = event.id

    db_session.commit()

    cleanup_database(db_session)

    db_session.expire_all()

    assert db_session.get(UsageEvent, event_id) is not None


def test_cleanup_preserves_conversations(
    db_session,
    privacy_user,
):

    conversation = Conversation(
        user_id=privacy_user.id,
        title="Preserve conversation",
        created_at=datetime.now(timezone.utc) - timedelta(days=365),
    )

    db_session.add(conversation)
    db_session.flush()

    conversation_id = conversation.id

    db_session.commit()

    cleanup_database(db_session)

    db_session.expire_all()

    assert db_session.get(
        Conversation,
        conversation_id,
    ) is not None
