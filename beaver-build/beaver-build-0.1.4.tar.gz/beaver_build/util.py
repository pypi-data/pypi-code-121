import asyncio
import contextlib
import logging
import os
import zlib


LOGGER = logging.getLogger(__name__)


@contextlib.contextmanager
def working_directory(directory):
    """
    Temporarily change the working directory using a context manager.
    """
    current = os.getcwd()
    os.chdir(directory)
    yield directory
    os.chdir(current)


class Crc32:
    """
    Compute the CRC32 using the :mod:`hashlib` interface.
    """
    def __init__(self, data: bytes = b"", value: int = 0) -> None:
        self.crc32 = zlib.crc32(data, value)

    def __int__(self):
        return self.crc32

    def update(self, data: bytes):
        self.crc32 = zlib.crc32(data, self.crc32)

    def digest(self) -> bytes:
        return self.crc32.to_bytes(4, 'big')

    def hexdigest(self) -> str:
        return self.digest().hex()


@contextlib.asynccontextmanager
async def noop_context(*args, **kwargs):
    yield


class Once:
    """
    Base class for executing something exactly once.
    """
    def __init__(self):
        self.future = None

    async def execute(self):
        raise NotImplementedError

    async def _wrapped_execute(self):
        if not self.future:
            LOGGER.debug("creating new future for %s", self)
            self.future = asyncio.Future()
            try:
                result = await self.execute()
                self.future.set_result(result)
            except Exception as ex:
                self.future.set_exception(ex)
        else:
            LOGGER.debug("awaiting existing future for %s", self)
        return await self.future

    def __await__(self):
        # See https://stackoverflow.com/a/57078217/1150961 for details.
        return (yield from self._wrapped_execute().__await__())
