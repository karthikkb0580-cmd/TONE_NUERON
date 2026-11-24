import uuid
from contextvars import ContextVar

from starlette.datastructures import MutableHeaders


request_id_context = ContextVar(
    "request_id",
    default=None,
)


class RequestIDMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())

        token = request_id_context.set(request_id)

        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        async def send_wrapper(message):

            if message["type"] == "http.response.start":

                headers = MutableHeaders(scope=message)
                headers["X-Request-ID"] = request_id

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)

        finally:
            request_id_context.reset(token)
