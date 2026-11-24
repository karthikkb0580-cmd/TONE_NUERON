import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.security_config import security_settings

from backend.app.middleware.request_id import (
    RequestIDMiddleware,
)

from backend.app.middleware.request_logging import (
    RequestLoggingMiddleware,
)

from backend.app.middleware.request_size import (
    RequestSizeMiddleware,
)

from backend.app.middleware.security_headers import (
    SecurityHeadersMiddleware,
)


def configure_middleware(app: FastAPI):

    app.add_middleware(
        RequestSizeMiddleware,
        max_size=security_settings.MAX_REQUEST_SIZE_BYTES,
    )

    app.add_middleware(
        CORSMiddleware,

        allow_origins=security_settings.allowed_origins,

        allow_credentials=False,

        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ],

        allow_headers=[
            "Authorization",
            "Content-Type",
        ],

        expose_headers=[
            "X-Request-ID",
            "X-Process-Time",
        ],

        max_age=600,
    )

    if security_settings.REQUEST_LOGGING_ENABLED:

        logging.getLogger(
            "tone_neuron.requests"
        ).setLevel(logging.INFO)

        app.add_middleware(
            RequestLoggingMiddleware
        )

    app.add_middleware(
        RequestIDMiddleware
    )

    app.add_middleware(
        SecurityHeadersMiddleware
    )
