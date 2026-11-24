import pytest

from backend.app.api.auth import get_current_user
from backend.app.main import app
from backend.app.models.user import User, UserPreferences
from backend.app.services.auth_service import hash_password


@pytest.fixture
def feature_user(db_session):
    user = User(
        email="features@example.com",
        username="feature_test",
        password_hash=hash_password("TestPassword123"),
        is_active=True,
        is_verified=True,
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

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        yield user
    finally:
        app.dependency_overrides.pop(get_current_user, None)

from backend.app.services.conversation_service import (
    create_conversation,
    add_message,
)


def test_feedback_management(
    client,
    db_session,
    feature_user,
):
    conversation = create_conversation(
        db_session,
        feature_user.id,
        "Feedback Test",
    )

    message = add_message(
        db_session,
        feature_user.id,
        conversation.id,
        "Test assistant response.",
        role="assistant",
    )

    response = client.post(
        "/api/v1/feedback",
        json={
            "message_id": str(message.id),
            "rating": 5,
            "reaction": "like",
        },
    )

    assert response.status_code == 200
    assert response.json()["rating"] == 5

    feedback_id = response.json()["id"]

    response = client.post(
        "/api/v1/feedback",
        json={
            "message_id": str(message.id),
            "rating": 2,
            "reaction": "dislike",
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == feedback_id

    response = client.get("/api/v1/feedback")

    assert len(response.json()) == 1

    response = client.delete(
        f"/api/v1/feedback/{feedback_id}"
    )

    assert response.status_code == 204


def test_feedback_rejects_user_message(
    client,
    db_session,
    feature_user,
):
    conversation = create_conversation(
        db_session,
        feature_user.id,
        "User Message Test",
    )

    message = add_message(
        db_session,
        feature_user.id,
        conversation.id,
        "User message.",
    )

    response = client.post(
        "/api/v1/feedback",
        json={
            "message_id": str(message.id),
            "rating": 5,
        },
    )

    assert response.status_code == 404


def test_feedback_validation(client, feature_user):
    from uuid import uuid4

    response = client.post(
        "/api/v1/feedback",
        json={
            "message_id": str(uuid4()),
            "rating": 10,
        },
    )

    assert response.status_code == 422

from uuid import uuid4


def test_desktop_device_management(
    client,
    feature_user,
):
    payload = {
        "installation_id": str(uuid4()),
        "device_name": "Development Laptop",
        "operating_system": "windows",
        "app_version": "2.0.0",
    }

    response = client.post(
        "/api/v1/desktop/devices/register",
        json=payload,
    )

    assert response.status_code == 200

    device = response.json()

    assert device["clipboard_enabled"] is False
    assert device["selected_text_enabled"] is False

    device_id = device["id"]

    response = client.post(
        "/api/v1/desktop/devices/register",
        json=payload,
    )

    assert response.json()["id"] == device_id

    url = f"/api/v1/desktop/devices/{device_id}"

    response = client.patch(
        url,
        json={"mascot_enabled": False},
    )

    assert response.status_code == 200
    assert response.json()["mascot_enabled"] is False

    assert client.get(url).status_code == 200

    response = client.post(f"{url}/heartbeat")

    assert response.status_code == 200

    response = client.get("/api/v1/desktop/devices")

    assert len(response.json()) == 1

    assert client.delete(url).status_code == 204
    assert client.get(url).status_code == 404


def test_device_validation(client, feature_user):
    response = client.post(
        "/api/v1/desktop/devices/register",
        json={
            "installation_id": str(uuid4()),
            "device_name": "Invalid Device",
            "operating_system": "unknown",
            "app_version": "2.0.0",
        },
    )

    assert response.status_code == 422


def test_device_isolation(
    client,
    db_session,
    feature_user,
):
    response = client.post(
        "/api/v1/desktop/devices/register",
        json={
            "installation_id": str(uuid4()),
            "device_name": "Private Device",
            "operating_system": "windows",
            "app_version": "2.0.0",
        },
    )

    assert response.status_code == 200

    device_id = response.json()["id"]

    other_user = User(
        email="otherdevice@example.com",
        username="other_device",
        password_hash=hash_password("TestPassword123"),
        is_active=True,
        is_verified=True,
    )

    db_session.add(other_user)
    db_session.commit()

    app.dependency_overrides[get_current_user] = lambda: other_user

    url = f"/api/v1/desktop/devices/{device_id}"

    assert client.get(url).status_code == 404
    assert client.delete(url).status_code == 404

from backend.app.services.analytics_service import record_usage


def test_analytics_summary(
    client,
    db_session,
    feature_user,
):
    record_usage(
        db_session,
        feature_user.id,
        feature="rewrite",
        language="en",
        detected_tone="professional",
        successful=True,
        processing_time_ms=120,
    )

    record_usage(
        db_session,
        feature_user.id,
        feature="grammar",
        language="hi",
        successful=False,
        processing_time_ms=80,
    )

    db_session.commit()

    response = client.get(
        "/api/v1/analytics/summary?days=7"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_requests"] == 2
    assert data["successful_requests"] == 1
    assert data["failed_requests"] == 1
    assert data["success_rate"] == 50.0
    assert data["average_processing_time_ms"] == 100.0
    assert len(data["daily_usage"]) == 7


def test_analytics_opt_out(
    client,
    db_session,
    feature_user,
):
    response = client.patch(
        "/api/v1/preferences",
        json={"analytics_enabled": False},
    )

    assert response.status_code == 200

    event = record_usage(
        db_session,
        feature_user.id,
        feature="rewrite",
    )

    db_session.commit()

    assert event is None

    response = client.get("/api/v1/analytics/summary")

    assert response.json()["total_requests"] == 0


def test_clear_analytics(
    client,
    db_session,
    feature_user,
):
    record_usage(
        db_session,
        feature_user.id,
        feature="tone",
    )

    db_session.commit()

    assert client.delete(
        "/api/v1/analytics"
    ).status_code == 400

    assert client.delete(
        "/api/v1/analytics?confirm=true"
    ).status_code == 204

    response = client.get("/api/v1/analytics/summary")

    assert response.json()["total_requests"] == 0


def test_feature_authentication(client):
    endpoints = [
        "/api/v1/feedback",
        "/api/v1/desktop/devices",
        "/api/v1/analytics/summary",
    ]

    for endpoint in endpoints:
        assert client.get(endpoint).status_code in (401, 403)
