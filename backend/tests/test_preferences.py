from backend.app.api.auth import get_current_user
from backend.app.main import app
from backend.app.models.user import User
from backend.app.services.auth_service import hash_password


def test_preferences_management(client, db_session):
    user = User(
        email="preferences@example.com",
        username="preferences_test",
        password_hash=hash_password("TestPassword123"),
        is_verified=True,
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.get("/api/v1/preferences")

        assert response.status_code == 200
        assert response.json()["preferred_language"] == "en"
        assert response.json()["conversation_history"] is False

        response = client.patch(
            "/api/v1/preferences",
            json={
                "preferred_language": "hi",
                "theme": "dark",
                "mascot_enabled": False,
            },
        )

        assert response.status_code == 200
        assert response.json()["preferred_language"] == "hi"
        assert response.json()["theme"] == "dark"
        assert response.json()["mascot_enabled"] is False

        response = client.get("/api/v1/preferences")

        assert response.json()["preferred_language"] == "hi"

        response = client.patch(
            "/api/v1/preferences",
            json={"theme": "invalid"},
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_preferences_requires_authentication(client):
    response = client.get("/api/v1/preferences")

    assert response.status_code in (401, 403)
