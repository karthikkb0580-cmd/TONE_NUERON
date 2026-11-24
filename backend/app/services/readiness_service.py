import asyncio

import httpx
import redis

from sqlalchemy import text
from starlette.concurrency import run_in_threadpool

from backend.app.core.config import settings
from backend.app.core.ml_config import ml_settings
from backend.app.database.session import SessionLocal


def check_database():

    try:

        with SessionLocal() as db:
            db.execute(text("SELECT 1"))

        return True

    except Exception:
        return False


def check_redis():

    client = None

    try:

        client = redis.Redis.from_url(
            settings.REDIS_URL,
            socket_connect_timeout=2,
            socket_timeout=2,
        )

        return bool(client.ping())

    except Exception:
        return False

    finally:
        if client is not None:
            client.close()


async def check_ml_service():

    try:

        url = str(
            ml_settings.ML_SERVICE_URL
        ).rstrip("/") + "/health"

        async with httpx.AsyncClient(
            timeout=3,
            follow_redirects=False,
        ) as client:

            response = await client.get(url)

            if response.status_code != 200:
                return False, False

            data = response.json()

            return (
                data.get("status") == "healthy",
                data.get("models_ready") is True,
            )

    except Exception:
        return False, False


async def check_readiness():

    database, redis_status, ml_status = await asyncio.gather(
        run_in_threadpool(check_database),
        run_in_threadpool(check_redis),
        check_ml_service(),
    )

    ml_connected, models_ready = ml_status

    return {
        "status": (
            "ready"
            if database and redis_status
            else "not_ready"
        ),
        "database": database,
        "redis": redis_status,
        "ml_service": ml_connected,
        "ml_models_ready": models_ready,
    }
