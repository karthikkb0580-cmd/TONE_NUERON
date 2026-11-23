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