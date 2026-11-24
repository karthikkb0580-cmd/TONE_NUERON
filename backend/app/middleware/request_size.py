from starlette.datastructures import Headers
from starlette.responses import JSONResponse


class RequestSizeMiddleware:

    def __init__(
        self,
        app,
        max_size: int = 1024 * 1024,
    ):
        self.app = app
        self.max_size = max_size

    async def reject(self, scope, receive, send):

        response = JSONResponse(
            status_code=413,
            content={
                "detail": "Request body is too large.",
                "code": "PAYLOAD_TOO_LARGE",
            },
        )

        await response(scope, receive, send)

    async def __call__(self, scope, receive, send):

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)

        content_length = headers.get("content-length")

        if content_length is not None:

            try:
                declared_size = int(content_length)

                if declared_size < 0:
                    raise ValueError()

            except ValueError:

                response = JSONResponse(
                    status_code=400,
                    content={
                        "detail": "Invalid Content-Length.",
                    },
                )

                await response(scope, receive, send)
                return

            if declared_size > self.max_size:

                await self.reject(scope, receive, send)
                return

        body = bytearray()

        while True:

            message = await receive()

            if message["type"] == "http.disconnect":
                return

            if message["type"] != "http.request":
                continue

            chunk = message.get("body", b"")

            if len(body) + len(chunk) > self.max_size:

                await self.reject(scope, receive, send)
                return

            body.extend(chunk)

            if not message.get("more_body", False):
                break

        delivered = False

        async def replay_receive():

            nonlocal delivered

            if not delivered:

                delivered = True

                return {
                    "type": "http.request",
                    "body": bytes(body),
                    "more_body": False,
                }

            return await receive()

        await self.app(scope, replay_receive, send)
