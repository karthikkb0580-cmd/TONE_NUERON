import pytest

from backend.app.api.auth import get_current_user
from backend.app.main import app
from backend.app.models.user import User, UserPreferences
from backend.app.services.auth_service import hash_password


@pytest.fixture
def conversation_user(db_session):
    user = User(
        email="conversation@example.com",
        username="conversation_test",
        password_hash=hash_password("TestPassword123"),
        is_verified=True,
        is_active=True,
    )

    db_session.add(user)
    db_session.flush()

    db_session.add(
        UserPreferences(
            user_id=user.id,
            conversation_history=True,
        )
    )

    db_session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        yield user
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_create_conversation(client, conversation_user):
    response = client.post(
        "/api/v1/conversations",
        json={"title": "Communication Coaching"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Communication Coaching"


def test_list_conversations(client, conversation_user):
    client.post(
        "/api/v1/conversations",
        json={"title": "First Conversation"},
    )

    response = client.get("/api/v1/conversations")

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_rename_conversation(client, conversation_user):
    created = client.post(
        "/api/v1/conversations",
        json={"title": "Old Title"},
    ).json()

    response = client.patch(
        f"/api/v1/conversations/{created['id']}",
        json={"title": "New Title"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_message_history(client, conversation_user):
    created = client.post(
        "/api/v1/conversations",
        json={"title": "Message Test"},
    ).json()

    url = f"/api/v1/conversations/{created['id']}/messages"

    response = client.post(
        url,
        json={
            "content": "Help me improve this message.",
            "language": "en",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "user"

    response = client.get(url)

    assert response.status_code == 200
    assert response.json()["total"] == 1


def test_delete_conversation(client, conversation_user):
    created = client.post(
        "/api/v1/conversations",
        json={"title": "Delete Test"},
    ).json()

    url = f"/api/v1/conversations/{created['id']}"

    assert client.delete(url).status_code == 204
    assert client.get(url).status_code == 404


def test_clear_history(client, conversation_user):
    client.post(
        "/api/v1/conversations",
        json={"title": "Clear Test"},
    )

    assert client.delete(
        "/api/v1/conversations"
    ).status_code == 400

    assert client.delete(
        "/api/v1/conversations?confirm=true"
    ).status_code == 204

    response = client.get("/api/v1/conversations")

    assert response.json()["total"] == 0


def test_history_disabled(
    client,
    conversation_user,
):
    response = client.patch(
        "/api/v1/preferences",
        json={"conversation_history": False},
    )

    assert response.status_code == 200

    response = client.post(
        "/api/v1/conversations",
        json={"title": "Private Conversation"},
    )

    assert response.status_code == 403


def test_conversation_isolation(
    client,
    db_session,
    conversation_user,
):
    created = client.post(
        "/api/v1/conversations",
        json={"title": "Private Data"},
    ).json()

    other_user = User(
        email="otherconversation@example.com",
        username="other_conversation",
        password_hash=hash_password("TestPassword123"),
        is_verified=True,
        is_active=True,
    )

    db_session.add(other_user)
    db_session.commit()

    app.dependency_overrides[get_current_user] = lambda: other_user

    url = f"/api/v1/conversations/{created['id']}"

    assert client.get(url).status_code == 404
    assert client.delete(url).status_code == 404

    response = client.get(f"{url}/messages")

    assert response.status_code == 404


def test_conversations_require_authentication(client):
    response = client.get("/api/v1/conversations")

    assert response.status_code in (401, 403)
