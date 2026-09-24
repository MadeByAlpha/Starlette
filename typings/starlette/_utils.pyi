from collections.abc import AsyncGenerator, Awaitable, Callable, Generator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from dataclasses import dataclass
from typing import Any, Protocol, TypeIs, TypeVar, overload

import anyio.abc
from starlette.types import Scope

__all__ = (
    "AwaitableCallable",
    "AwaitableOrContextManager",
    "AwaitableOrContextManagerWrapper",
    "SupportsAsyncClose",
    "create_collapsing_task_group",
    "get_route_path",
    "is_async_callable",
    "parse_host_header",
)

@dataclass(frozen=True, slots=True)
class ParsedHost:
    host: str
    port: str | None
    @property
    def authority(self) -> str:
        ...

    @property
    def is_valid_port(self) -> bool:
        ...

type AwaitableCallable[**P, T] = Callable[P, Awaitable[T]]

@overload
def is_async_callable[**P, T](obj: Callable[P, Awaitable[T]]) -> TypeIs[Callable[P, Awaitable[T]]]: ...
@overload
def is_async_callable(obj: object) -> TypeIs[Callable[..., Awaitable[Any]]]: ...

__T_co = TypeVar("__T_co", covariant=True)
class AwaitableOrContextManager(Awaitable[__T_co], AbstractAsyncContextManager[__T_co], Protocol[__T_co]):
    ...


class SupportsAsyncClose(Protocol):
    async def close(self) -> None:
        ...


class AwaitableOrContextManagerWrapper[SupportsAsyncCloseType: SupportsAsyncClose]:
    __slots__ = ...
    def __init__(self, aw: Awaitable[SupportsAsyncCloseType]) -> None:
        ...

    def __await__(self) -> Generator[Any, None, SupportsAsyncCloseType]:
        ...

    async def __aenter__(self) -> SupportsAsyncCloseType:
        ...

    async def __aexit__(self, *args: object) -> bool | None:
        ...


@asynccontextmanager
async def create_collapsing_task_group() -> AsyncGenerator[anyio.abc.TaskGroup]:
    ...

def parse_host_header(host_header: str | None) -> ParsedHost | None:
    """Parse `host_header` into its host and port components.

    The host preserves brackets around IP literals. Invalid headers produce `None`.
    """

def get_route_path(scope: Scope) -> str:
    ...

