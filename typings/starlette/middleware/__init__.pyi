from collections.abc import Awaitable, Callable, Iterator
from typing import Any, ParamSpec, Protocol

P = ParamSpec("P")
type _Scope = Any
type _Receive = Callable[[], Awaitable[Any]]
type _Send = Callable[[Any], Awaitable[None]]
type _ASGIApp = Callable[[_Scope, _Receive, _Send], Awaitable[None]]
class _MiddlewareFactory(Protocol[P]):
    def __call__(self, app: _ASGIApp, /, *args: P.args, **kwargs: P.kwargs) -> _ASGIApp:
        ...



class Middleware:
    def __init__(self, cls: _MiddlewareFactory[P], *args: P.args, **kwargs: P.kwargs) -> None:
        ...

    def __iter__(self) -> Iterator[Any]:
        ...




