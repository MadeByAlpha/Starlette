from abc import ABC, abstractmethod

from .._base import Routes
from ..routes import RouteAttachMixin, WebSocketRouteAttachMixin
from ._routes import HostMixin, MountMixin

if __debug__ and __import__("typing").TYPE_CHECKING:
    from typing import Any

    from starlette.datastructures import URLPath


class Routable(
    Routes,
    RouteAttachMixin,
    WebSocketRouteAttachMixin,
    MountMixin,
    HostMixin,
    ABC
):  # type: ignore[ty:inconsistent-mro]
    @abstractmethod
    def url_path_for(self, name: str, /, **path_params: Any) -> URLPath:
        ...
