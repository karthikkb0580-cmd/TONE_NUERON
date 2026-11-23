import hashlib

import redis

from fastapi import HTTPException

from backend.app.core.config import settings


redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
)


def get_login_key(email: str) -> str:
    normalized_email = email.strip().lower()

    email_hash = hashlib.sha256(
        normalized_email.encode("utf-8")
    ).hexdigest()

    return f"security:login:failed:{email_hash}"


def check_login_allowed(email: str) -> None:
    key = get_login_key(email)

    attempts = redis_client.get(key)

    if attempts is None:
        return

    if int(attempts) >= settings.LOGIN_MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail=(
                "Too many failed login attempts. "
                "Please try again later."
            ),
        )


def record_failed_login(email: str) -> None:
    key = get_login_key(email)

    # Increment the failed-attempt counter.
    attempts = redis_client.incr(key)

    # Set expiration when the first failure occurs.
    if attempts == 1:
        redis_client.expire(
            key,
            settings.LOGIN_FAILURE_WINDOW_SECONDS,
        )


def clear_failed_logins(email: str) -> None:
    key = get_login_key(email)

    redis_client.delete(key)