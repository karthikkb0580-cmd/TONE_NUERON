import logging
import re

from time import perf_counter

from fastapi import HTTPException

from backend.app.database.session import SessionLocal
from backend.app.schemas.ai import AIRequest, MLRequest, AIFeature
from backend.app.services.ml_client import call_ml_service
from backend.app.services.analytics_service import record_usage


logger = logging.getLogger("tone_neuron.ai")


ALLOWED_TONES = {
    "professional",
    "friendly",
    "casual",
    "formal",
    "empathetic",
    "concise",
    "confident",
    "polite",
    "aggressive",
    "neutral",
    "assertive",
    "passive",
    "sarcastic",
}


def safe_language(value):

    if value and re.fullmatch(
        r"[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8}){0,2}",
        value,
    ):
        return value.lower()

    return None


def save_usage(
    user_id,
    feature,
    language,
    detected_tone,
    successful,
    processing_time_ms,
):

    try:

        with SessionLocal() as db:

            record_usage(
                db=db,
                user_id=user_id,
                feature=feature,
                language=safe_language(language),
                detected_tone=(
                    detected_tone
                    if detected_tone in ALLOWED_TONES
                    else None
                ),
                successful=successful,
                processing_time_ms=processing_time_ms,
            )

            db.commit()

    except Exception:

        logger.warning("Unable to record AI usage metadata.")


async def process_ai_request(
    user_id,
    feature: AIFeature,
    data: AIRequest,
):

    from starlette.concurrency import run_in_threadpool

    if feature == "translate" and not data.target_language:

        raise HTTPException(
            status_code=422,
            detail="Target language is required.",
        )

    started = perf_counter()

    try:

        result = await call_ml_service(
            MLRequest(
                feature=feature,
                **data.model_dump(),
            )
        )

    except HTTPException:

        duration = int(
            (perf_counter() - started) * 1000
        )

        await run_in_threadpool(
            save_usage,
            user_id,
            feature,
            data.language,
            None,
            False,
            duration,
        )

        raise

    duration = int(
        (perf_counter() - started) * 1000
    )

    await run_in_threadpool(
        save_usage,
        user_id,
        feature,
        result.detected_language or data.language,
        result.detected_tone,
        True,
        duration,
    )

    return result
