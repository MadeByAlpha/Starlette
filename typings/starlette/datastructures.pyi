from collections.abc import (
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    MutableMapping,
    Sequence,
    ValuesView,
)
from typing import Any, BinaryIO, Literal, NamedTuple, Self, TypeVar
from urllib.parse import SplitResult

from starlette.types import Scope

class Address(NamedTuple):
    host: str
    port: int


__KeyType = TypeVar("__KeyType")
__ValueType_co = TypeVar("__ValueType_co", covariant=True)
class URL:
    def __init__(self, url: str = ..., scope: Scope | None = ..., **components: Any) -> None:
        ...

    @property
    def components(self) -> SplitResult:
        ...

    @property
    def scheme(self) -> str:
        ...

    @property
    def netloc(self) -> str:
        ...

    @property
    def path(self) -> str:
        ...

    @property
    def query(self) -> str:
        ...

    @property
    def fragment(self) -> str:
        ...

    @property
    def username(self) -> str | None:
        ...

    @property
    def password(self) -> str | None:
        ...

    @property
    def hostname(self) -> str | None:
        ...

    @property
    def port(self) -> int | None:
        ...

    @property
    def is_secure(self) -> bool:
        ...

    def replace(self, **kwargs: Any) -> URL:
        ...

    def include_query_params(self, **kwargs: Any) -> URL:
        ...

    def replace_query_params(self, **kwargs: Any) -> URL:
        ...

    def remove_query_params(self, keys: str | Sequence[str]) -> URL:
        ...

    def __eq__(self, other: object) -> bool:
        ...


class URLPath(str):
    """
    A URL path string that may also hold an associated protocol and/or host.
    Used by the routing to return `url_path_for` matches.
    """

    __slots__ = ("host", "protocol")

    protocol: Literal["http", "websocket", ""]
    host: str

    def __new__(cls, path: str, protocol: Literal["http", "websocket", ""] = ..., host: str = ...) -> Self:
        ...

    def __init__(self, path: str, protocol: Literal["http", "websocket", ""] = ..., host: str = ...) -> None:
        ...

    def make_absolute_url(self, base_url: str | URL) -> URL:
        ...



class Secret:
    """
    Holds a string value that should not be revealed in tracebacks etc.
    You should cast the value to `str` at the point it is required.
    """
    def __init__(self, value: str) -> None:
        ...

    def __bool__(self) -> bool:
        ...


class CommaSeparatedStrings(Sequence[str]):
    def __init__(self, value: str | Sequence[str]) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __getitem__(self, index: int | slice) -> Any:
        ...

    def __iter__(self) -> Iterator[str]:
        ...


class ImmutableMultiDict(Mapping[__KeyType, __ValueType_co]):
    _dict: dict[__KeyType, __ValueType_co]
    def __init__(self, *args: ImmutableMultiDict[__KeyType, __ValueType_co] | Mapping[__KeyType, __ValueType_co] | Iterable[tuple[__KeyType, __ValueType_co]], **kwargs: Any) -> None:
        ...

    def getlist(self, key: Any) -> list[__ValueType_co]:
        ...

    def keys(self) -> KeysView[__KeyType]:
        ...

    def values(self) -> ValuesView[__ValueType_co]:
        ...

    def items(self) -> ItemsView[__KeyType, __ValueType_co]:
        ...

    def multi_items(self) -> list[tuple[__KeyType, __ValueType_co]]:
        ...

    def __getitem__(self, key: __KeyType) -> __ValueType_co:
        ...

    def __contains__(self, key: Any) -> bool:
        ...

    def __iter__(self) -> Iterator[__KeyType]:
        ...

    def __len__(self) -> int:
        ...

    def __eq__(self, other: object) -> bool:
        ...


class MultiDict(ImmutableMultiDict[Any, Any]):
    def __setitem__(self, key: Any, value: Any) -> None:
        ...

    def __delitem__(self, key: Any) -> None:
        ...

    def pop(self, key: Any, default: Any = ...) -> Any:
        ...

    def popitem(self) -> tuple[Any, Any]:
        ...

    def poplist(self, key: Any) -> list[Any]:
        ...

    def clear(self) -> None:
        ...

    def setdefault(self, key: Any, default: Any = ...) -> Any:
        ...

    def setlist(self, key: Any, values: list[Any]) -> None:
        ...

    def append(self, key: Any, value: Any) -> None:
        ...

    def update(self, *args: MultiDict | Mapping[Any, Any] | list[tuple[Any, Any]], **kwargs: Any) -> None:
        ...



class QueryParams(ImmutableMultiDict[str, str]):
    """
    An immutable multidict.
    """
    def __init__(self, *args: ImmutableMultiDict[Any, Any] | Mapping[Any, Any] | list[tuple[Any, Any]] | str | bytes, **kwargs: Any) -> None:
        ...


class UploadFile:
    """
    An uploaded file included as part of the request data.
    """
    def __init__(self, file: BinaryIO, *, size: int | None = ..., filename: str | None = ..., headers: Headers | None = ...) -> None:
        ...

    @property
    def content_type(self) -> str | None:
        ...

    async def write(self, data: bytes) -> None:
        ...

    async def read(self, size: int = ...) -> bytes:
        ...

    async def seek(self, offset: int) -> None:
        ...

    async def close(self) -> None:
        ...


class FormData(ImmutableMultiDict[str, UploadFile | str]):
    """
    An immutable multidict, containing both file uploads and text input.
    """
    def __init__(self, *args: FormData | Mapping[str, str | UploadFile] | list[tuple[str, str | UploadFile]], **kwargs: str | UploadFile) -> None:
        ...

    async def close(self) -> None:
        ...


class Headers(Mapping[str, str]):
    """
    An immutable, case-insensitive multidict.
    """
    def __init__(self, headers: Mapping[str, str] | None = ..., raw: list[tuple[bytes, bytes]] | None = ..., scope: MutableMapping[str, Any] | None = ...) -> None:
        ...

    @property
    def raw(self) -> list[tuple[bytes, bytes]]:
        ...

    # noinspection method-overriding
    def keys(self) -> list[str]:
        ...

    # noinspection method-overriding
    def values(self) -> list[str]:
        ...

    # noinspection method-overriding
    def items(self) -> list[tuple[str, str]]:
        ...

    def getlist(self, key: str) -> list[str]:
        ...

    def mutablecopy(self) -> MutableHeaders:
        ...

    def __getitem__(self, key: str) -> str:
        ...

    def __contains__(self, key: Any) -> bool:
        ...

    def __iter__(self) -> Iterator[Any]:
        ...

    def __len__(self) -> int:
        ...

    def __eq__(self, other: object) -> bool:
        ...


class MutableHeaders(Headers):
    def __setitem__(self, key: str, value: str) -> None:
        """
        Set the header `key` to `value`, removing any duplicate entries.
        Retains insertion order.
        """

    def __delitem__(self, key: str) -> None:
        """
        Remove the header `key`.
        """

    def __ior__(self, other: Mapping[str, str]) -> Self:
        ...

    def __or__(self, other: Mapping[str, str]) -> MutableHeaders:
        ...

    @property
    def raw(self) -> list[tuple[bytes, bytes]]:
        ...

    def setdefault(self, key: str, value: str) -> str:
        """
        If the header `key` does not exist, then set it to `value`.
        Returns the header value.
        """

    def update(self, other: Mapping[str, str]) -> None:
        ...

    def append(self, key: str, value: str) -> None:
        """
        Append a header, preserving any duplicate entries.
        """

    def add_vary_header(self, vary: str) -> None:
        ...


class State(Mapping[str, Any]):
    """
    An object that can be used to store arbitrary state.

    Used for `request.state` and `app.state`.
    """
    _state: dict[str, Any]
    def __init__(self, state: dict[str, Any] | None = ...) -> None:
        ...

    def __setattr__(self, key: Any, value: Any) -> None:
        ...

    def __getattr__(self, key: Any) -> Any:
        ...

    def __delattr__(self, key: Any) -> None:
        ...

    def __getitem__(self, key: str) -> Any:
        ...

    def __setitem__(self, key: str, value: Any) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __iter__(self) -> Iterator[str]:
        ...

    def __len__(self) -> int:
        ...
