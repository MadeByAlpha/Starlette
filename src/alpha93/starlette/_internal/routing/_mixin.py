from abc import ABC

from ._base import BaseRoute, Routes


class RouterMixin(Routes, ABC):
    pass


class AttachableRoute[T: RouterMixin](BaseRoute, ABC):
    pass
