# -*- coding: UTF-8 -*-

from ast import literal_eval
from datetime import datetime, timezone, date
from decimal import Decimal
from functools import wraps
from os import makedirs
from os.path import dirname, realpath, isdir, basename
from typing import Union, Generator
from zipfile import ZipFile

from .constants import INSTANCES


class MetaSingleton(type):
    """
    Singleton metaclass (for non-strict class).
    Restrict object to only one instance per runtime.
    """

    def __call__(cls, *args, **kwargs):
        if hasattr(cls, "_instance") is False:
            cls._instance = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instance


def singleton(cls):
    """
    Singleton decorator (for metaclass).
    Restrict object to only one instance per runtime.
    """

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in INSTANCES:
            # a strong reference to the object is required.
            instance = cls(*args, **kwargs)
            INSTANCES[cls] = instance
        return INSTANCES[cls]
    return wrapper


def today():
    """Return current date as a `datetime.date` object."""
    return date.today()


def timestamp(fmt: str = "%Y-%m-%d %H:%M:%S.%f") -> str:
    """:returns: an aware localized and formatted `datetime` string object."""
    local = get_local()
    return local.strftime(fmt)


def get_local() -> datetime:
    """:returns: an aware localized datetime object."""
    utc = get_utc()
    return utc.astimezone()


def get_utc() -> datetime:
    """:returns: an UTC `datetime` object."""
    return datetime.now(timezone.utc)


def ensure_folder(path: str):
    """Read the file path and recursively create the folder structure if needed."""
    folder_path: str = dirname(realpath(path))
    make_dirs(folder_path)


def make_dirs(path: str):
    """Checks if a folder path exists and creates it if not."""
    if isdir(path) is False:
        makedirs(path)


def encode(value: Union[str, bytes], encoding: str = "UTF-8") -> bytes:
    """Encode the string `value` with UTF-8."""
    if isinstance(value, str):
        value = value.encode(encoding)
    return value


def decode(value: Union[bytes, str], encoding: str = "UTF-8") -> str:
    """Decode the bytes-like object `value` with UTF-8."""
    if isinstance(value, bytes):
        value = value.decode(encoding)
    return value


def to_bytes(value: Union[Decimal, bytes], encoding: str = "UTF-8") -> bytes:
    if isinstance(value, Decimal):
        value = encode(str(value), encoding)
    return value


def to_decimal(value: Union[bytes, Decimal], encoding: str = "UTF-8") -> Decimal:
    if isinstance(value, bytes):
        value = Decimal(decode(value, encoding))
    return value


def evaluate(value: str):
    """Transform a string to an appropriate data type."""
    try:
        value = literal_eval(value)
    except (SyntaxError, ValueError):
        pass
    return value


def archive(file_path: str, data: Union[Generator, str]):
    """Archive `data` to the given `file_path`."""
    with ZipFile(file_path, "w") as zip_handle:
        if isinstance(data, Generator) is True:
            for file in data:
                path, name = file, basename(file)
                zip_handle.write(path, name)
        else:
            path, name = data, basename(data)
            zip_handle.write(path, name)


def del_prefix(target: str, prefix: str):
    """
    If `target` starts with the `prefix` string and `prefix` is not empty,
    return string[len(prefix):].
    Otherwise, return a copy of the original string.
    """
    if (len(prefix) > 0) and (target.startswith(prefix) is True):
        try:  # python >= 3.9
            target = target.removeprefix(prefix)
        except AttributeError:  # python <= 3.7
            target = target[len(prefix):]

    return target


def del_suffix(target: str, suffix: str):
    """
    If `target` ends with the `suffix` string and `suffix` is not empty,
    return string[:-len(suffix)].
    Otherwise, return a copy of the original string.
    """
    if (len(suffix) > 0) and (target.endswith(suffix) is True):
        try:  # python >= 3.9
            target = target.removesuffix(suffix)
        except AttributeError:  # python <= 3.7
            target = target[:-len(suffix)]

    return target
