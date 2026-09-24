import functools
import inspect
from abc import ABC

from alpha93.commons.types import any_object, constructor

from starlette._exception_handler import wrap_app_handling_exceptions
from starlette._utils import get_route_path, is_async_callable
from starlette.concurrency import run_in_threadpool
from starlette.datastructures import URLPath

from ._match import Match, NoMatchFound
from ._mixin import AttachableRoute, RouterMixin

if __debug__ and __import__("typing").TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Collection, Sequence
    from typing import Any, Protocol

    from alpha93.commons.types import AwaitableOr

    from starlette.middleware import Middleware
    from starlette.requests import Request
    from starlette.responses import Response
    from starlette.types import ASGIApp, Receive, Scope, Send
    from starlette.websockets import WebSocket

    class SupportsCall(Protocol):
        def __call__(self, *args, **kwargs) -> Any: ...


get_name: Callable[[SupportsCall], str] = lambda endpoint: getattr(endpoint, "__name__", endpoint.__class__.__name__)


class RouteAttachMixin(RouterMixin, ABC):
    def add_route(
        self,
        path: str,
        endpoint: Callable[[Request], AwaitableOr[Response]],
        methods: Collection[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
    ) -> None:  # pragma: no cover
        route = constructor[Route](Route.__init__)(
            path,
            endpoint=endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )
        self.routes.append(route)


class Route(AttachableRoute[RouteAttachMixin]):
    @staticmethod
    def request_response(func: Callable[[Request], AwaitableOr[Response]], /) -> ASGIApp:
        """
        Takes a function or coroutine `func(request) -> response`,
        and returns an ASGI application.
        """
        f: Callable[[Request], Awaitable[Response]] = any_object(
            func if is_async_callable(func) else functools.partial(run_in_threadpool, func)
        )

        async def app(scope: Scope, receive: Receive, send: Send) -> None:
            request = Request(scope, receive, send)

            async def app(scope: Scope, receive: Receive, send: Send) -> None:
                response = await f(request)
                await response(scope, receive, send)

            await wrap_app_handling_exceptions(app, request)(scope, receive, send)

        return app

    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        methods: Collection[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        middleware: Sequence[Middleware] | None = None,
        max_body_size: int | None = None,
    ) -> None:
        assert path.startswith("/"), "Routed paths must start with '/'"
        self.path = path
        self.endpoint = endpoint
        self.name = get_name(endpoint) if name is None else name
        self.include_in_schema = include_in_schema

        endpoint_handler = endpoint
        while isinstance(endpoint_handler, functools.partial):
            endpoint_handler = endpoint_handler.func
        if inspect.isfunction(endpoint_handler) or inspect.ismethod(endpoint_handler):
            # Endpoint is function or method. Treat it as `func(request) -> response`.
            self.app = self.request_response(endpoint)
            if methods is None:
                methods = ["GET"]
        else:
            # Endpoint is a class. Treat it as ASGI.
            self.app = endpoint

        if middleware is not None:
            for cls, args, kwargs in reversed(middleware):
                self.app = cls(self.app, *args, **kwargs)

        if max_body_size is not None:
            from starlette.middleware.body_limit import RequestBodyLimitMiddleware

            self.app = RequestBodyLimitMiddleware(self.app, max_body_size=max_body_size)

        if methods is None:
            self.methods = None
        else:
            self.methods = {method.upper() for method in methods}
            if "GET" in self.methods:
                self.methods.add("HEAD")

        self.path_regex, self.path_format, self.param_convertors = self.compile_path(
            path
        )

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        path_params: dict[str, Any]
        if scope["type"] == "http":
            route_path = get_route_path(scope)
            match = self.path_regex.match(route_path)
            if match:
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(value)
                path_params = dict(scope.get("path_params", {}))
                path_params.update(matched_params)
                child_scope = {"endpoint": self.endpoint, "path_params": path_params}
                if self.methods and scope["method"] not in self.methods:
                    return Match.PARTIAL, child_scope
                else:
                    return Match.FULL, child_scope
        return Match.NONE, {}

    def url_path_for(self, name: str, /, **path_params: Any) -> URLPath:
        seen_params = set(path_params.keys())
        expected_params = set(self.param_convertors.keys())

        if name != self.name or seen_params != expected_params:
            raise NoMatchFound(name, path_params)

        path, remaining_params = self.replace_params(
            self.path_format, self.param_convertors, path_params
        )
        assert not remaining_params
        return URLPath(path=path, protocol="http")

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.methods and scope["method"] not in self.methods:
            headers = {"Allow": ", ".join(self.methods)}
            if "app" in scope:
                from starlette.exceptions import HTTPException

                raise HTTPException(status_code=405, headers=headers)
            else:
                from starlette.responses import PlainTextResponse

                response = PlainTextResponse("Method Not Allowed", status_code=405, headers=headers)
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, Route)
            and self.path == other.path
            and self.endpoint == other.endpoint
            and self.methods == other.methods
        )

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        methods = sorted(self.methods or [])
        path, name = self.path, self.name
        return f"{class_name}(path={path!r}, name={name!r}, methods={methods!r})"


class WebSocketRouteAttachMixin(RouterMixin, ABC):
    def add_websocket_route(
        self,
        path: str,
        endpoint: Callable[[WebSocket], Awaitable[None]],
        name: str | None = None,
    ) -> None:  # pragma: no cover
        route = constructor[WebSocketRoute](WebSocketRoute.__init__)(
            path, endpoint=endpoint, name=name
        )
        self.routes.append(route)


class WebSocketRoute(AttachableRoute[WebSocketRouteAttachMixin]):
    @staticmethod
    def websocket_session(func: Callable[[WebSocket], Awaitable[None]], /) -> ASGIApp:
        """
        Takes a coroutine `func(session)`, and returns an ASGI application.
        """
        # assert asyncio.iscoroutinefunction(func), "WebSocket endpoints must be async"

        async def app(scope: Scope, receive: Receive, send: Send) -> None:
            session = WebSocket(scope, receive=receive, send=send)

            async def app(scope: Scope, receive: Receive, send: Send) -> None:
                await func(session)

            await wrap_app_handling_exceptions(app, session)(scope, receive, send)

        return app

    def __init__(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        name: str | None = None,
        middleware: Sequence[Middleware] | None = None,
    ) -> None:
        assert path.startswith("/"), "Routed paths must start with '/'"
        self.path = path
        self.endpoint = endpoint
        self.name = get_name(endpoint) if name is None else name

        endpoint_handler = endpoint
        while isinstance(endpoint_handler, functools.partial):
            endpoint_handler = endpoint_handler.func
        if inspect.isfunction(endpoint_handler) or inspect.ismethod(endpoint_handler):
            # Endpoint is function or method. Treat it as `func(websocket)`.
            self.app = self.websocket_session(endpoint)
        else:
            # Endpoint is a class. Treat it as ASGI.
            self.app = endpoint

        if middleware is not None:
            for cls, args, kwargs in reversed(middleware):
                self.app = cls(self.app, *args, **kwargs)

        self.path_regex, self.path_format, self.param_convertors = self.compile_path(
            path
        )

    def matches(self, scope: Scope) -> tuple[Match, Scope]:
        path_params: dict[str, Any]
        if scope["type"] == "websocket":
            route_path = get_route_path(scope)
            match = self.path_regex.match(route_path)
            if match:
                matched_params = match.groupdict()
                for key, value in matched_params.items():
                    matched_params[key] = self.param_convertors[key].convert(value)
                path_params = dict(scope.get("path_params", {}))
                path_params.update(matched_params)
                child_scope = {"endpoint": self.endpoint, "path_params": path_params}
                return Match.FULL, child_scope
        return Match.NONE, {}

    def url_path_for(self, name: str, /, **path_params: Any) -> URLPath:
        seen_params = set(path_params.keys())
        expected_params = set(self.param_convertors.keys())

        if name != self.name or seen_params != expected_params:
            raise NoMatchFound(name, path_params)

        path, remaining_params = self.replace_params(
            self.path_format, self.param_convertors, path_params
        )
        assert not remaining_params
        return URLPath(path=path, protocol="websocket")

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.app(scope, receive, send)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, WebSocketRoute)
            and self.path == other.path
            and self.endpoint == other.endpoint
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path!r}, name={self.name!r})"
