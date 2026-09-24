from collections.abc import Callable, Sequence
from typing import Any, ParamSpec

from starlette.requests import HTTPConnection

def has_required_scope(conn: HTTPConnection, scopes: Sequence[str]) -> bool:
    ...

def requires[**P](scopes: str | Sequence[str], status_code: int = ..., redirect: str | None = ...) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
    ...

class AuthenticationError(Exception):
    ...


class AuthenticationBackend:
    async def authenticate(self, conn: HTTPConnection) -> tuple[AuthCredentials, BaseUser] | None:
        ...



class AuthCredentials:
    def __init__(self, scopes: Sequence[str] | None = ...) -> None:
        ...



class BaseUser:
    @property
    def is_authenticated(self) -> bool:
        ...

    @property
    def display_name(self) -> str:
        ...

    @property
    def identity(self) -> str:
        ...



class SimpleUser(BaseUser):
    def __init__(self, username: str) -> None:
        ...

    @property
    def is_authenticated(self) -> bool:
        ...

    @property
    def display_name(self) -> str:
        ...

    @property
    def identity(self) -> str:
        ...



class UnauthenticatedUser(BaseUser):
    @property
    def is_authenticated(self) -> bool:
        ...

    @property
    def display_name(self) -> str:
        ...

    @property
    def identity(self) -> str:
        ...



