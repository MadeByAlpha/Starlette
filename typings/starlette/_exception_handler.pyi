from typing import Any

from starlette.requests import Request
from starlette.types import ASGIApp, ExceptionHandler
from starlette.websockets import WebSocket

type ExceptionHandlers = dict[Any, ExceptionHandler]
type StatusHandlers = dict[int, ExceptionHandler]

def wrap_app_handling_exceptions(app: ASGIApp, conn: Request | WebSocket) -> ASGIApp:
    ...

__all__ = (
    "ExceptionHandlers",
    "StatusHandlers",
    "wrap_app_handling_exceptions",
)
