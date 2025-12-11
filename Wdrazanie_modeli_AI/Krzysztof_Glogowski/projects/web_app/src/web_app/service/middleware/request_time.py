import time

from starlette.datastructures import MutableHeaders


class RequestProcessingTimeMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        start = time.perf_counter()

        async def send_with_extra_headers(message):
            if message["type"] == "http.response.start":
                elapsed = time.perf_counter() - start
                headers = MutableHeaders(scope=message)
                # All custom headers MUST start with X-
                headers.append("X-Request-Processing-Time", f"{elapsed}")

            await send(message)

        await self.app(scope, receive, send_with_extra_headers)
        return None
