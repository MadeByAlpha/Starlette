from collections.abc import Collection

from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send

ALL_METHODS = ...
SAFELISTED_HEADERS = ...
class CORSMiddleware:
    def __init__(self, app: ASGIApp, allow_origins: Collection[str] = ..., allow_methods: Collection[str] = ..., allow_headers: Collection[str] = ..., allow_credentials: bool = ..., allow_origin_regex: str | None = ..., allow_private_network: bool = ..., expose_headers: Collection[str] = ..., max_age: int = ...) -> None:
        ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ...

    def is_allowed_origin(self, origin: str) -> bool:
        ...

    def preflight_response(self, request_headers: Headers) -> Response:
        ...

    async def simple_response(self, scope: Scope, receive: Receive, send: Send, request_headers: Headers) -> None:
        ...

    async def send(self, message: Message, send: Send, request_headers: Headers) -> None:
        ...

    @staticmethod
    def allow_explicit_origin(headers: MutableHeaders, origin: str) -> None:
        ...



