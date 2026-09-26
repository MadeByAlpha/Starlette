from collections.abc import Awaitable, Callable, Mapping, MutableMapping
from contextlib import AbstractAsyncContextManager
from typing import Any, Protocol

from starlette.requests import Request
from starlette.responses import Response
from starlette.websockets import WebSocket

__all__ = (
    "ASGIApp",
    "ASGIAppType",
    "ExceptionHandler",
    "HTTPExceptionHandler",
    "Lifespan",
    "Message",
    "Receive",
    "Scope",
    "Send",
    "StatefulLifespan",
    "StatelessLifespan",
    "WebSocketExceptionHandler",
)

type Scope = MutableMapping[str, Any]
type Message = MutableMapping[str, Any]
type Receive = Callable[[], Awaitable[Message]]
type Send = Callable[[Message], Awaitable[None]]

type ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]
class ASGIAppType(Protocol):
    async def __call__(self, scope: Scope, receive: Receive, send: Send, /) -> None:
        """
        A route may be used in isolation as a stand-alone ASGI app.
        This is a somewhat contrived case, as they'll almost always be used
        within a Router, but could be useful for some tooling and minimal apps.
        """

type StatelessLifespan[AppType] = Callable[[AppType], AbstractAsyncContextManager[None]]
type StatefulLifespan[AppType] = Callable[[AppType], AbstractAsyncContextManager[Mapping[str, Any]]]
type Lifespan[AppType] = StatelessLifespan[AppType] | StatefulLifespan[AppType]

type HTTPExceptionHandler = Callable[[Request, Exception], Awaitable[Response]]
type WebSocketExceptionHandler = Callable[[WebSocket, Exception], Awaitable[None]]
type ExceptionHandler = HTTPExceptionHandler | WebSocketExceptionHandler
