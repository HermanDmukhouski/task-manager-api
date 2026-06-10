import logging
import time

from starlette.types import ASGIApp
from starlette.types import Message
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

logger = logging.getLogger("api")


class LoggingMiddleware:
    """Чистый ASGI-middleware: без накладных расходов BaseHTTPMiddleware."""

    def __init__(self, app: ASGIApp) -> None:
        self._app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self._app(scope, receive, send)
            return

        start = time.monotonic()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self._app(scope, receive, send_wrapper)
        finally:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.info(
                "%s %s -> %s (%.1fms)",
                scope["method"],
                scope["path"],
                status_code,
                elapsed_ms,
            )
