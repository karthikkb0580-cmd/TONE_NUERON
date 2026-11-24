import secrets

from fastapi import Header, HTTPException

from app.core.config import settings


def verify_internal_api_key(
    x_internal_api_key: str | None = Header(default=None),
):

    expected = settings.ML_SERVICE_API_KEY.get_secret_value()

    if not x_internal_api_key:

        raise HTTPException(
            status_code=401,
            detail="Internal authentication required.",
        )

    if not secrets.compare_digest(
        x_internal_api_key.encode("utf-8"),
        expected.encode("utf-8"),
    ):

        raise HTTPException(
            status_code=401,
            detail="Invalid internal credentials.",
        )
