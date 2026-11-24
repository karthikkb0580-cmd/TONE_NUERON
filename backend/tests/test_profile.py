from backend.app.api.auth import get_current_user
from backend.app.main import app
from backend.app.models.user import User
from backend.app.services.auth_service import hash_password


def test_profile_management(client, db_session):
    user = User(
        email="profile@example.com",
        username="profile_test",
        password_hash=hash_password("TestPassword123"),
        is_verified=True,
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    try:
        response = client.get("/api/v1/profile")

        assert response.status_code == 200
        assert response.json()["display_name"] == "profile_test"

        response = client.patch(
            "/api/v1/profile",
            json={
                "display_name": "Neuro User",
                "bio": "Learning AI and technology",
            },
        )

        assert response.status_code == 200
        assert response.json()["display_name"] == "Neuro User"

        response = client.get("/api/v1/profile")

        assert response.json()["bio"] == "Learning AI and technology"

    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_profile_requires_authentication(client):
    response = client.get("/api/v1/profile")

    assert response.status_code in (401, 403)
