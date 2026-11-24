import asyncio

import httpx
import pytest

from fastapi import HTTPException

from backend.app.main import app
from backend.app.schemas.ai import MLRequest
from backend.app.services.ml_client import call_ml_service


def test_ai_routes_registered():

    paths = set(app.openapi()["paths"])

    features = [
        "analyze",
        "tone",
        "sentiment",
        "emotion",
        "rewrite",
        "grammar",
        "translate",
        "suggest-reply",
        "summarize",
        "expand",
        "coach",
        "toxicity",
    ]

    for feature in features:
        assert f"/api/v1/ai/{feature}" in paths


def test_ai_authentication(client):

    response = client.post(
        "/api/v1/ai/tone",
        json={"text": "Hello"},
    )

    assert response.status_code in (401, 403)


def mock_http_client(monkeypatch, handler):

    original_client = httpx.AsyncClient

    def factory(*args, **kwargs):

        return original_client(
            transport=httpx.MockTransport(handler),
            *args,
            **kwargs,
        )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        factory,
    )


def test_ml_success(monkeypatch):

    def handler(request):

        assert "X-Internal-API-Key" in request.headers

        return httpx.Response(
            200,
            json={
                "feature": "tone",
                "detected_tone": "professional",
                "confidence": 0.95,
                "model_name": "mock-test-model",
                "processing_time_ms": 10,
            },
        )

    mock_http_client(monkeypatch, handler)

    result = asyncio.run(
        call_ml_service(
            MLRequest(
                feature="tone",
                text="Please review this.",
            )
        )
    )

    assert result.detected_tone == "professional"


@pytest.mark.parametrize(
    "upstream_status,expected_status",
    [
        (501, 501),
        (429, 503),
        (401, 502),
        (500, 502),
    ],
)
def test_ml_error_mapping(
    monkeypatch,
    upstream_status,
    expected_status,
):

    def handler(request):

        return httpx.Response(
            upstream_status,
            json={"detail": "Mock failure"},
        )

    mock_http_client(monkeypatch, handler)

    with pytest.raises(HTTPException) as error:

        asyncio.run(
            call_ml_service(
                MLRequest(
                    feature="tone",
                    text="Hello",
                )
            )
        )

    assert error.value.status_code == expected_status


def test_ml_timeout(monkeypatch):

    def handler(request):

        raise httpx.ReadTimeout(
            "Mock timeout",
            request=request,
        )

    mock_http_client(monkeypatch, handler)

    with pytest.raises(HTTPException) as error:

        asyncio.run(
            call_ml_service(
                MLRequest(
                    feature="tone",
                    text="Hello",
                )
            )
        )

    assert error.value.status_code == 504


def test_ml_connection_failure(monkeypatch):

    def handler(request):

        raise httpx.ConnectError(
            "Mock connection failure",
            request=request,
        )

    mock_http_client(monkeypatch, handler)

    with pytest.raises(HTTPException) as error:

        asyncio.run(
            call_ml_service(
                MLRequest(
                    feature="tone",
                    text="Hello",
                )
            )
        )

    assert error.value.status_code == 503


def test_ml_invalid_response(monkeypatch):

    def handler(request):

        return httpx.Response(
            200,
            json={"unexpected": "response"},
        )

    mock_http_client(monkeypatch, handler)

    with pytest.raises(HTTPException) as error:

        asyncio.run(
            call_ml_service(
                MLRequest(
                    feature="tone",
                    text="Hello",
                )
            )
        )

    assert error.value.status_code == 502


def test_ml_wrong_feature(monkeypatch):

    def handler(request):

        return httpx.Response(
            200,
            json={
                "feature": "sentiment",
                "model_name": "mock-test-model",
            },
        )

    mock_http_client(monkeypatch, handler)

    with pytest.raises(HTTPException) as error:

        asyncio.run(
            call_ml_service(
                MLRequest(
                    feature="tone",
                    text="Hello",
                )
            )
        )

    assert error.value.status_code == 502
