from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from backend.app.middleware.request_size import RequestSizeMiddleware


def test_security_headers(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_request_id(client):
    response = client.get("/health")

    assert UUID(response.headers["X-Request-ID"])


def test_unique_request_ids(client):
    first = client.get("/health")
    second = client.get("/health")

    assert first.headers["X-Request-ID"] != second.headers["X-Request-ID"]


def test_request_processing_time(client):
    response = client.get("/health")

    assert float(response.headers["X-Process-Time"]) >= 0


def test_cors_allowed_origin(client):
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:5173"},
    )

    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"


def test_cors_disallowed_origin(client):
    response = client.get(
        "/health",
        headers={"Origin": "https://untrusted.example"},
    )

    assert "Access-Control-Allow-Origin" not in response.headers


def test_cors_preflight(client):
    response = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,authorization",
        },
    )

    assert response.status_code == 200


def test_oversized_request(client):
    response = client.post(
        "/api/v1/auth/login",
        content=b"x" * (1024 * 1024 + 1),
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 413
    assert response.json()["code"] == "PAYLOAD_TOO_LARGE"


def test_sensitive_response_cache_control(client):
    response = client.get("/api/v1/auth/me")

    assert response.headers["Cache-Control"] == "no-store"


def test_security_headers_on_error(client):
    response = client.get("/nonexistent-endpoint")

    assert response.status_code == 404
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "X-Request-ID" in response.headers


def test_actual_body_size_limit():
    app = FastAPI()

    app.add_middleware(RequestSizeMiddleware, max_size=100)

    @app.post("/upload")
    async def upload(request: Request):
        body = await request.body()
        return {"size": len(body)}

    with TestClient(app) as test_client:
        response = test_client.post(
            "/upload",
            content=b"x" * 101,
            headers={"Content-Length": "10"},
        )

        assert response.status_code == 413


def test_normal_request_body():
    app = FastAPI()

    app.add_middleware(RequestSizeMiddleware, max_size=100)

    @app.post("/upload")
    async def upload(request: Request):
        body = await request.body()
        return {"size": len(body)}

    with TestClient(app) as test_client:
        response = test_client.post(
            "/upload",
            content=b"hello",
        )

        assert response.status_code == 200
        assert response.json()["size"] == 5
