from contextvars import ContextVar
from uuid import uuid4

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Receive, Scope, Send

CORRELATION_ID: ContextVar[str] = ContextVar("correlation_id", default="---")


class CorrelationIdMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
        self.header_name = "X-Correlation-ID"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        CORRELATION_ID.set(uuid4().hex)

        headers = MutableHeaders(scope=scope)
        headers.append(self.header_name, CORRELATION_ID.get())

        await self.app(scope, receive, send)
        return
