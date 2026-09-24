from urllib.parse import parse_qsl, urlencode

from .multidict import ImmutableMultiDict

if __debug__ and __import__("typing").TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


class QueryParams(ImmutableMultiDict[str, str]):
    """
    An immutable multidict.
    """

    def __init__(
        self,
        *args: ImmutableMultiDict[Any, Any] | Mapping[Any, Any] | list[tuple[Any, Any]] | str | bytes,
        **kwargs: Any,
    ) -> None:
        assert len(args) < 2, "Too many arguments."

        value = args[0] if args else []

        if isinstance(value, str):
            super().__init__(parse_qsl(value, keep_blank_values=True), **kwargs)
        elif isinstance(value, bytes):
            super().__init__(parse_qsl(value.decode("latin-1"), keep_blank_values=True), **kwargs)
        else:
            super().__init__(*args, **kwargs)  # type: ignore[arg-type, ty:invalid-argument-type]
        self._list = [(str(k), str(v)) for k, v in self._list]
        self._dict = {str(k): str(v) for k, v in self._dict.items()}

    def __str__(self) -> str:
        return urlencode(self._list)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        query_string = str(self)
        return f"{class_name}({query_string!r})"
