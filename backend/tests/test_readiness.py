from backend.app.api import readiness


def test_readiness_success(client, monkeypatch):

    async def mock_check():
        return {
            "status": "ready",
            "database": True,
            "redis": True,
            "ml_service": True,
            "ml_models_ready": False,
        }

    monkeypatch.setattr(
        readiness,
        "check_readiness",
        mock_check,
    )

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_readiness_database_failure(client, monkeypatch):

    async def mock_check():
        return {
            "status": "not_ready",
            "database": False,
            "redis": True,
            "ml_service": True,
            "ml_models_ready": False,
        }

    monkeypatch.setattr(
        readiness,
        "check_readiness",
        mock_check,
    )

    response = client.get("/ready")

    assert response.status_code == 503


def test_readiness_redis_failure(client, monkeypatch):

    async def mock_check():
        return {
            "status": "not_ready",
            "database": True,
            "redis": False,
            "ml_service": True,
            "ml_models_ready": False,
        }

    monkeypatch.setattr(
        readiness,
        "check_readiness",
        mock_check,
    )

    response = client.get("/ready")

    assert response.status_code == 503


def test_readiness_ml_unavailable(client, monkeypatch):

    async def mock_check():
        return {
            "status": "ready",
            "database": True,
            "redis": True,
            "ml_service": False,
            "ml_models_ready": False,
        }

    monkeypatch.setattr(
        readiness,
        "check_readiness",
        mock_check,
    )

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json()["ml_service"] is False
