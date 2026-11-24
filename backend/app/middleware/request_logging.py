import json
import logging
import time
from datetime import datetime, timezone

from starlette.datastructures import MutableHeaders


logger = logging.getLogger("tone_neuron.requests")


class RequestLoggingMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started = time.perf_counter()
        status_code = 500

        async def send_wrapper(message):

            nonlocal status_code

            if message["type"] == "http.response.start":

                status_code = message["status"]

                duration = time.perf_counter() - started

                headers = MutableHeaders(scope=message)

                headers["X-Process-Time"] = (
                    f"{duration:.6f}"
                )

            await send(message)

        try:

            await self.app(scope, receive, send_wrapper)

        finally:

            duration_ms = round(
                (time.perf_counter() - started) * 1000,
                2,
            )

            route = scope.get("route")

            route_template = getattr(
                route,
                "path",
                "unmatched",
            )

            event = {
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),

                "request_id": scope.get(
                    "state", {}
                ).get("request_id"),

                "method": scope.get("method"),
                "route": route_template,
                "status_code": status_code,
                "duration_ms": duration_ms,
            }

            logger.info(
                json.dumps(event)
            )
