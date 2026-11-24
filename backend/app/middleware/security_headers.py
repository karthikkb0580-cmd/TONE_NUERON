from starlette.datastructures import MutableHeaders


class SecurityHeadersMiddleware:

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):

            if message["type"] == "http.response.start":

                headers = MutableHeaders(scope=message)

                headers["X-Content-Type-Options"] = "nosniff"
                headers["X-Frame-Options"] = "DENY"
                headers["Referrer-Policy"] = "no-referrer"

                headers["Permissions-Policy"] = (
                    "camera=(), microphone=(), geolocation=()"
                )

                headers["Cross-Origin-Opener-Policy"] = "same-origin"
                headers["X-Permitted-Cross-Domain-Policies"] = "none"

                if scope.get("path", "").startswith("/api/"):
                    headers["Cache-Control"] = "no-store"

            await send(message)

        await self.app(scope, receive, send_wrapper)
