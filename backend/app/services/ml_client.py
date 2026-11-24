import httpx

from fastapi import HTTPException
from pydantic import ValidationError

from backend.app.core.ml_config import ml_settings
from backend.app.schemas.ai import MLRequest, AIResponse


async def call_ml_service(data: MLRequest) -> AIResponse:

    url = (
        str(ml_settings.ML_SERVICE_URL).rstrip("/")
        + "/internal/v1/inference"
    )

    timeout = httpx.Timeout(
        ml_settings.ML_SERVICE_TIMEOUT_SECONDS,
        connect=ml_settings.ML_SERVICE_CONNECT_TIMEOUT_SECONDS,
    )

    headers = {
        "X-Internal-API-Key": (
            ml_settings.ML_SERVICE_API_KEY.get_secret_value()
        ),
        "Content-Type": "application/json",
    }

    try:

        async with httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=False,
        ) as client:

            response = await client.post(
                url,
                json=data.model_dump(mode="json"),
                headers=headers,
            )

    except httpx.TimeoutException:

        raise HTTPException(
            status_code=504,
            detail="AI service request timed out.",
        )

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable.",
        )

    if response.status_code == 501:

        raise HTTPException(
            status_code=501,
            detail="This AI feature is not implemented yet.",
        )

    if response.status_code == 429:

        raise HTTPException(
            status_code=503,
            detail="AI service is currently busy.",
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=502,
            detail="AI service returned an unexpected response.",
        )

    try:

        result = AIResponse.model_validate(response.json())

    except (ValidationError, ValueError):

        raise HTTPException(
            status_code=502,
            detail="AI service returned an invalid response.",
        )

    if result.feature != data.feature:

        raise HTTPException(
            status_code=502,
            detail="AI service returned an incorrect feature.",
        )

    return result
