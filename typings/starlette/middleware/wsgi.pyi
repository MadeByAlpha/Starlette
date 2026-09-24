from collections.abc import Callable, MutableMapping
from typing import Any

from anyio.abc import ObjectReceiveStream, ObjectSendStream

from starlette.types import Receive, Scope, Send

def build_environ(scope: Scope, body: bytes) -> dict[str, Any]:
    """
    Builds a scope and request body into a WSGI environ object.
    """

class WSGIMiddleware:
    def __init__(self, app: Callable[..., Any]) -> None:
        ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ...



class WSGIResponder:
    stream_send: ObjectSendStream[MutableMapping[str, Any]]
    stream_receive: ObjectReceiveStream[MutableMapping[str, Any]]
    def __init__(self, app: Callable[..., Any], scope: Scope) -> None:
        ...

    async def __call__(self, receive: Receive, send: Send) -> None:
        ...

    async def sender(self, send: Send) -> None:
        ...

    def start_response(self, status: str, response_headers: list[tuple[str, str]], exc_info: Any = ...) -> None:
        ...

    def wsgi(self, environ: dict[str, Any], start_response: Callable[..., Any]) -> None:
        ...



