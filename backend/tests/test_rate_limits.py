import uuid

import pytest
from redis import Redis

from backend.app.core.config import settings


def clear_test_rate_limits():

    redis_client = Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )

    try:
        keys = list(
            redis_client.scan_iter(
                match="LIMITS:LIMITER/testclient*"
            )
        )

        if keys:
            redis_client.delete(*keys)

    finally:
        redis_client.close()


@pytest.fixture(autouse=True)
def reset_rate_limits():

    clear_test_rate_limits()

    yield

    clear_test_rate_limits()


def test_registration_rate_limit(client):

    unique_id = uuid.uuid4().hex[:12]

    for attempt in range(3):

        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": f"user{attempt}_{unique_id}@example.com",
                "username": f"user{attempt}_{unique_id}",
                "password": "StrongPassword123!",
            },
        )

        assert response.status_code == 201

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"blocked_{unique_id}@example.com",
            "username": f"blocked_{unique_id}",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 429


def test_login_rate_limit(client):

    email = f"security_{uuid.uuid4().hex}@example.com"

    for attempt in range(5):

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": email,
                "password": "WrongPassword123!",
            },
        )

        assert response.status_code == 401

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 429