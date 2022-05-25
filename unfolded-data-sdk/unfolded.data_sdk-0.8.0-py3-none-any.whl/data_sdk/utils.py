import gzip
import os
import shutil
from typing import IO, Any, Callable, Iterable, Optional

import requests
from requests.exceptions import HTTPError

from unfolded.data_sdk.errors import AuthenticationError, DataSDKError


def get_fileobj_length(fileobj: IO) -> int:
    """Get length of file object"""
    pos = fileobj.tell()
    fileobj.seek(0, os.SEEK_END)
    length = fileobj.tell()
    fileobj.seek(pos)
    return length


def read_fileobj_chunks(
    fileobj: IO[bytes], chunk_size: int, callback: Optional[Callable[[int], Any]] = None
) -> Iterable[bytes]:
    """Generator to read a file object by chunks"""
    while True:
        data = fileobj.read(chunk_size)
        if not data:
            break

        if callback:
            callback(len(data))

        yield data


# BinaryIO is supposed to be an alias for IO[bytes], but for some reason this
# fails with BinaryIO? Seems related to https://stackoverflow.com/q/62745734 but
# that's supposed to be fixed already.
def compress_fileobj(file_in: IO[bytes], file_out: IO[bytes], **kwargs: Any) -> None:
    """Apply gzip compression to file object

    Args:
        file_in: readable file object (in binary mode) with data to be compressed.
        file_out: writable file object (in binary mode) where compressed data should be written.
        **kwargs: keyword arguments to pass to gzip.open
    """
    with gzip.open(file_out, "wb", **kwargs) as gzipf:
        shutil.copyfileobj(file_in, gzipf)


def raise_for_status(r: requests.Response) -> None:
    """Check valid response, raising custom error for invalid authorization"""
    try:
        r.raise_for_status()
    except HTTPError as e:
        # Re-raise authentication error with better error message
        if r.status_code in (401, 403):
            raise AuthenticationError("Invalid Access Token") from e

        try:
            msg = r.json()["message"]
            raise DataSDKError(msg) from e
        except:
            pass

        raise e
