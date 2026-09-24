from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, TypeVar, cast

if __debug__ and TYPE_CHECKING:
    from collections.abc import ItemsView, Iterable, Iterator, KeysView, ValuesView

__KeyType = TypeVar("__KeyType")
# Mapping keys are invariant but their values are covariant since
# you can only read them
# that is, you can't do `Mapping[str, Animal]()["fido"] = Dog()`
__ValueType_co = TypeVar("__ValueType_co", covariant=True)


class CommaSeparatedStrings(Sequence[str]):
    def __init__(self, value: str | Sequence[str]):
        if isinstance(value, str):
            from shlex import shlex

            splitter = shlex(value, posix=True)
            splitter.whitespace = ","
            splitter.whitespace_split = True
            self._items = [item.strip() for item in splitter]
        else:
            self._items = list(value)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int | slice) -> Any:
        return self._items[index]

    def __iter__(self) -> Iterator[str]:
        return iter(self._items)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        items = [item for item in self]
        return f"{class_name}({items!r})"

    def __str__(self) -> str:
        return ", ".join(repr(item) for item in self)

# noinspection unbound-local-variable
class ImmutableMultiDict(Mapping[__KeyType, __ValueType_co]):
    _dict: dict[__KeyType, __ValueType_co]

    def __init__(
        self,
        *args: Iterable[tuple[__KeyType, __ValueType_co]] | ImmutableMultiDict[__KeyType, __ValueType_co] | Mapping[__KeyType, __ValueType_co],
        **kwargs: Any,
    ) -> None:
        assert len(args) < 2, "Too many arguments."

        value: Any = args[0] if args else []
        if kwargs:
            value = ImmutableMultiDict(value).multi_items() + ImmutableMultiDict(kwargs).multi_items()

        if not value:
            _items: list[tuple[Any, Any]] = []
        elif hasattr(value, "multi_items"):
            value = cast("ImmutableMultiDict[__KeyType, __ValueType_co]", value)
            _items = list(value.multi_items())
        elif hasattr(value, "items"):
            value = cast("Mapping[__KeyType, __ValueType_co]", value)
            _items = list(value.items())
        else:
            value = cast("list[tuple[Any, Any]]", value)
            _items = list(value)

        self._dict = {k: v for k, v in _items}
        self._list = _items

    # noinspection variance
    def getlist(self, key: Any) -> list[__ValueType_co]:    # type: ignore[ty:invalid-generic-class]
        return [item_value for item_key, item_value in self._list if item_key == key]

    def keys(self) -> KeysView[__KeyType]:
        return self._dict.keys()

    def values(self) -> ValuesView[__ValueType_co]:
        return self._dict.values()

    def items(self) -> ItemsView[__KeyType, __ValueType_co]:
        return self._dict.items()

    # noinspection variance
    def multi_items(self) -> list[tuple[__KeyType, __ValueType_co]]:    # type: ignore[ty:invalid-generic-class]
        return list(self._list)

    def __getitem__(self, key: __KeyType) -> __ValueType_co:
        return self._dict[key]

    def __contains__(self, key: Any) -> bool:
        return key in self._dict

    def __iter__(self) -> Iterator[__KeyType]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._dict)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return sorted(self._list) == sorted(other._list)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        items = self.multi_items()
        return f"{class_name}({items!r})"


class MultiDict(ImmutableMultiDict[__KeyType, __ValueType_co]):
    # noinspection variance
    def __setitem__(self, key: __KeyType, value: __ValueType_co) -> None:   # type: ignore[ty:invalid-generic-class]
        self.setlist(key, [value])

    def __delitem__(self, key: __KeyType) -> None:
        self._list = [(k, v) for k, v in self._list if k != key]
        del self._dict[key]

    def pop(self, key: __KeyType, default: Any = None) -> Any:
        self._list = [(k, v) for k, v in self._list if k != key]
        return self._dict.pop(key, default)

    def popitem(self) -> tuple[Any, Any]:
        key, value = self._dict.popitem()
        self._list = [(k, v) for k, v in self._list if k != key]
        return key, value

    def poplist(self, key: __KeyType) -> list[Any]:
        values = [v for k, v in self._list if k == key]
        self.pop(key)
        return values

    def clear(self) -> None:
        self._dict.clear()
        self._list.clear()

    def setdefault(self, key: __KeyType, default: Any = None) -> Any:
        if key not in self:
            self._dict[key] = default
            self._list.append((key, default))

        return self[key]

    def setlist(self, key: __KeyType, values: list[Any]) -> None:
        if not values:
            self.pop(key, None)
        else:
            existing_items = [(k, v) for (k, v) in self._list if k != key]
            self._list = existing_items + [(key, value) for value in values]
            self._dict[key] = values[-1]

    # noinspection variance
    def append(self, key: __KeyType, value: __ValueType_co) -> None:    # type: ignore[ty:invalid-generic-class]
        self._list.append((key, value))
        self._dict[key] = value

    def update(
        self,
        *args: MultiDict | Mapping[Any, Any] | list[tuple[Any, Any]],
        **kwargs: Any,
    ) -> None:
        value = MultiDict(*args, **kwargs)
        existing_items = [(k, v) for (k, v) in self._list if k not in value]
        self._list = existing_items + value.multi_items()
        self._dict.update(value)
