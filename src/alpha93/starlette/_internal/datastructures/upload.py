from __future__ import annotations

from starlette.concurrency import run_in_threadpool

from .headers import Headers
from .multidict import ImmutableMultiDict

if __debug__ and __import__("typing").TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import BinaryIO


class UploadFile:
    """
    An uploaded file included as part of the request data.
    """

    def __init__(
        self,
        file: BinaryIO,
        *,
        size: int | None = None,
        filename: str | None = None,
        headers: Headers | None = None,
    ) -> None:
        self.filename = filename
        self.file = file
        self.size = size
        self.headers = headers or Headers()

        # Capture max size from SpooledTemporaryFile if one is provided. This slightly speeds up future checks.
        # Note 0 means unlimited mirroring SpooledTemporaryFile's __init__
        self._max_mem_size = getattr(self.file, "_max_size", 0)

    @property
    def content_type(self) -> str | None:
        return self.headers.get("content-type", None)

    @property
    def _in_memory(self) -> bool:
        # check for SpooledTemporaryFile._rolled
        rolled_to_disk = getattr(self.file, "_rolled", True)
        return not rolled_to_disk

    def _will_roll(self, size_to_add: int) -> bool:
        # If we're not in_memory then we will always roll
        if not self._in_memory:
            return True

        # Check for SpooledTemporaryFile._max_size
        future_size = self.file.tell() + size_to_add
        return bool(future_size > self._max_mem_size) if self._max_mem_size else False

    async def write(self, data: bytes) -> None:
        new_data_len = len(data)
        if self.size is not None:
            self.size += new_data_len

        if self._will_roll(new_data_len):
            await run_in_threadpool(self.file.write, data)
        else:
            self.file.write(data)

    async def read(self, size: int = -1) -> bytes:
        if self._in_memory:
            return self.file.read(size)
        return await run_in_threadpool(self.file.read, size)

    async def seek(self, offset: int) -> None:
        if self._in_memory:
            self.file.seek(offset)
        else:
            await run_in_threadpool(self.file.seek, offset)

    async def close(self) -> None:
        if self._in_memory:
            self.file.close()
        else:
            await run_in_threadpool(self.file.close)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(filename={self.filename!r}, size={self.size!r}, headers={self.headers!r})"


class FormData(ImmutableMultiDict[str, UploadFile | str]):
    """
    An immutable multidict, containing both file uploads and text input.
    """

    def __init__(
        self,
        *args: FormData | Mapping[str, str | UploadFile] | list[tuple[str, str | UploadFile]],
        **kwargs: str | UploadFile,
    ) -> None:
        super().__init__(*args, **kwargs)

    async def close(self) -> None:
        for key, value in self.multi_items():
            if isinstance(value, UploadFile):
                await value.close()
