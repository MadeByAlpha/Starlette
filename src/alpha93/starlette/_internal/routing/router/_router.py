from __future__ import annotations

from typing import override

from starlette._utils import get_route_path

from .._match import Match, NoMatchFound
from ._base import Routable

if __debug__ and __import__("typing").TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Self

    from starlette.datastructures import URL, URLPath
    from starlette.middleware import Middleware
    from starlette.types import ASGIApp, Lifespan, Receive, Scope, Send

    from .._base import BaseRoute


class _DefaultLifespan:
    def __init__(self, router: Router):
        self._router = router

    async def __aenter__(self) -> None:
        pass

    async def __aexit__(self, *exc_info: object) -> None:
        pass

    def __call__(self, app: object) -> Self:
        return self


class Router(Routable):
    @property
    def routes(self) -> list[BaseRoute]:
        return self.__routes

    def __init__(
        self,
        routes: Sequence[BaseRoute] | None = None,
        redirect_slashes: bool = True,
        default: ASGIApp | None = None,
        # the generic to Lifespan[AppType] is the type of the top level application
        # which the router cannot know statically, so we use Any
        lifespan: Lifespan[Any] | None = None,
        *,
        middleware: Sequence[Middleware] | None = None,
        max_body_size: int | None = None,
    ) -> None:
        self.__routes = [] if routes is None else list(routes)
        self.redirect_slashes = redirect_slashes
        self.default = self.not_found if default is None else default

        if lifespan is None:
            self.lifespan_context: Lifespan[Any] = _DefaultLifespan(self)
        else:
            if __debug__:
                import inspect

                assert not inspect.isasyncgenfunction(lifespan), "async generator function lifespans are deprecated, use an @contextlib.asynccontextmanager function instead"
                assert not inspect.isgeneratorfunction(lifespan), "generator function lifespans are deprecated, use an @contextlib.asynccontextmanager function instead"

                self.lifespan_context = lifespan

            self.middleware_stack = self.app
            if middleware:
                for cls, args, kwargs in reversed(middleware):
                    self.middleware_stack = cls(self.middleware_stack, *args, **kwargs)

            if max_body_size is not None:
                from starlette.middleware.body_limit import RequestBodyLimitMiddleware

                self.middleware_stack = RequestBodyLimitMiddleware(
                    self.middleware_stack, max_body_size=max_body_size
                )

    @override
    def url_path_for(self, name: str, /, **path_params: Any) -> URLPath:
        for route in self.routes:
            try:
                return route.url_path_for(name, **path_params)
            except NoMatchFound:
                pass
        raise NoMatchFound(name, path_params)

    async def not_found(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "websocket":
            from starlette.websockets import WebSocketClose

            websocket_close = WebSocketClose()
            await websocket_close(scope, receive, send)
            return

        # If we're running inside a starlette application then raise an
        # exception, so that the configurable exception handler can deal with
        # returning the response. For plain ASGI apps, just return the response.
        if "app" in scope:
            from starlette.exceptions import HTTPException

            raise HTTPException(status_code=404)
        else:
            from starlette.responses import PlainTextResponse

            response = PlainTextResponse("Not Found", status_code=404)
        await response(scope, receive, send)

    async def lifespan(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        Handle ASGI lifespan messages, which allows us to manage application
        startup and shutdown events.
        """
        started = False
        app: Any = scope.get("app")
        await receive()
        try:
            async with self.lifespan_context(app) as maybe_state:
                if maybe_state is not None:
                    if "state" not in scope:
                        raise RuntimeError(
                            'The server does not support "state" in the lifespan scope.'
                        )
                    scope["state"].update(maybe_state)
                await send({"type": "lifespan.startup.complete"})
                started = True
                await receive()
        except BaseException:
            import traceback

            exc_text = traceback.format_exc()
            if started:
                await send({"type": "lifespan.shutdown.failed", "message": exc_text})
            else:
                await send({"type": "lifespan.startup.failed", "message": exc_text})
            raise
        else:
            await send({"type": "lifespan.shutdown.complete"})

    async def app(self, scope: Scope, receive: Receive, send: Send) -> None:
        assert scope["type"] in ("http", "websocket", "lifespan")

        if "router" not in scope:
            scope["router"] = self

        if scope["type"] == "lifespan":
            await self.lifespan(scope, receive, send)
            return

        partial = None

        for route in self.routes:
            # Determine if any route matches the incoming scope,
            # and hand over to the matching route if found.
            match, child_scope = route.matches(scope)
            if match == Match.FULL:
                scope.update(child_scope)
                await route.handle(scope, receive, send)
                return
            elif match == Match.PARTIAL and partial is None:
                partial = route
                partial_scope = child_scope

        if partial is not None:
            # Handle partial matches. These are cases where an endpoint is
            # able to handle the request, but is not a preferred option.
            # We use this in particular to deal with "405 Method Not Allowed".
            scope.update(partial_scope)
            await partial.handle(scope, receive, send)
            return

        route_path = get_route_path(scope)
        if scope["type"] == "http" and self.redirect_slashes and route_path != "/":
            redirect_scope = dict(scope)
            if route_path.endswith("/"):
                redirect_scope["path"] = redirect_scope["path"].rstrip("/")
            else:
                redirect_scope["path"] = redirect_scope["path"] + "/"

            for route in self.routes:
                match, child_scope = route.matches(redirect_scope)
                if match != Match.NONE:
                    from starlette.responses import RedirectResponse

                    redirect_url = URL(scope=redirect_scope)
                    response = RedirectResponse(url=str(redirect_url))
                    await response(scope, receive, send)
                    return

        await self.default(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """
        The main entry point to the Router class.
        """
        await self.middleware_stack(scope, receive, send)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Router) and self.routes == other.routes
