from collections.abc import AsyncIterator, Callable, Iterable
from typing import ParamSpec, TypeVar

async def run_until_first_complete(*args: tuple[Callable, dict]) -> None:
    ...

async def run_in_threadpool[**P, T](func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
    ...

class _StopIteration(Exception):
    ...


async def iterate_in_threadpool[T](iterator: Iterable[T]) -> AsyncIterator[T]:
    ...

