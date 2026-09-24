import zlib
from typing import NoReturn

import anyio.lowlevel

from starlette.types import ASGIApp, Message, Receive, Scope, Send

DEFAULT_EXCLUDED_CONTENT_TYPES = ...
_gzip_capacity_limiter: anyio.lowlevel.RunVar[anyio.CapacityLimiter] = ...
class GZipMiddleware:
    def __init__(self, app: ASGIApp, minimum_size: int = ..., compresslevel: int = ..., thread_minimum_size: int = ..., *, exclude_content_types: tuple[str, ...] = ...) -> None:
        ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ...



class IdentityResponder:
    content_encoding: str
    def __init__(self, app: ASGIApp, minimum_size: int, *, exclude_content_types: tuple[str, ...] = ...) -> None:
        ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ...

    async def send_with_compression(self, message: Message) -> None:
        ...

    async def apply_compression(self, body: bytes, *, more_body: bool) -> bytes:
        """Apply compression on the response body.

        If more_body is False, the compression stream is finalized. Compression
        resources are only allocated once a body is actually compressed.
        """



class GZipResponder(IdentityResponder):
    content_encoding = ...
    def __init__(self, app: ASGIApp, minimum_size: int, compresslevel: int = ..., *, thread_minimum_size: int = ..., exclude_content_types: tuple[str, ...] = ...) -> None:
        ...

    @property
    def compressor(self) -> zlib._Compress:
        ...

    async def apply_compression(self, body: bytes, *, more_body: bool) -> bytes:
        ...



async def unattached_send(message: Message) -> NoReturn:
    ...

