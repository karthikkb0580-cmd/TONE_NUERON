from fastapi import FastAPI

from backend.app.api.auth import router as auth_router
from backend.app.api.otp import router as otp_router
from backend.app.api.password_reset import (
    router as password_reset_router,
)
from backend.app.api.sessions import router as sessions_router
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from backend.app.core.rate_limit import limiter


app = FastAPI(
    title="Tone Neuron API",
    description="AI Communication Coach Backend",
    version="2.0.0",
)


app.include_router(auth_router)
app.include_router(otp_router)
app.include_router(password_reset_router)
app.include_router(sessions_router)
app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


@app.get("/")
def root():
    return {
        "message": "Tone Neuron API is running",
        "status": "ok",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }
from fastapi import Request
from fastapi.responses import JSONResponse
from backend.app.core.exceptions import EmailDeliveryError


@app.exception_handler(EmailDeliveryError)
async def email_delivery_exception_handler(
    request: Request,
    exc: EmailDeliveryError,
):
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "Email delivery is temporarily unavailable. "
                "Please try requesting a new code."
            ),
            "code": "EMAIL_DELIVERY_FAILED",
        },
    )

from backend.app.api.profile import router as profile_router
from backend.app.api.preferences import router as preferences_router

app.include_router(profile_router)
app.include_router(preferences_router)

from backend.app.api.account import router as account_router

app.include_router(account_router)
