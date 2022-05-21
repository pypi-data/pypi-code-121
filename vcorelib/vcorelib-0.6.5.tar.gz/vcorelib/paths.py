"""
Common path manipulation utilities.
"""

# built-in
from hashlib import md5 as _md5
from pathlib import Path as _Path
from typing import Iterable as _Iterable
from typing import Optional as _Optional
from typing import Union as _Union

# internal
from vcorelib import DEFAULT_ENCODING as _DEFAULT_ENCODING

Pathlike = _Union[_Path, str, None]


def normalize(path: Pathlike) -> _Path:
    """Normalize an input that could be a path into a path."""
    return (
        _Path("." if path is None else path)
        if not isinstance(path, _Path)
        else path
    )


def get_file_name(path: Pathlike, maxsplit: int = -1) -> str:
    """
    From a path to a file, get the name of the file. Use 'maxsplit' to control
    how many suffixes are considered part of the name or the extension.
    """
    split = normalize(path).name.split(".", maxsplit=maxsplit)
    if len(split) > 1:
        pieces = split[:-1]
    else:
        pieces = [split[0]]
    return ".".join(pieces)


def get_file_ext(path: Pathlike, maxsplit: int = -1) -> str:
    """
    From a path to a file, get the file's extension. Use 'maxsplit' to control
    how many suffixes are considered part of the name or the extension.
    """
    return normalize(path).name.split(".", maxsplit=maxsplit)[-1]


def str_md5_hex(data: str, encoding: str = _DEFAULT_ENCODING) -> str:
    """Get an md5 hex string from string data."""
    return _md5(bytes(data, encoding)).hexdigest()


def file_md5_hex(path: Pathlike) -> str:
    """Get an md5 hex string for a file by path."""
    with normalize(path).open("rb") as stream:
        return _md5(stream.read()).hexdigest()


def find_file(
    path: Pathlike,
    search_paths: _Iterable[Pathlike] = None,
    include_cwd: bool = False,
    relative_to: Pathlike = None,
) -> _Optional[_Path]:
    """Combines a few simple strategies to locate a file on disk."""

    path = normalize(path)

    # If path is absolute we can't search for it.
    if path.is_absolute():
        if path.is_file():
            return path
        return None

    to_check = list(search_paths) if search_paths else []

    # Check the working directory if it was specified.
    if include_cwd:
        to_check.append(_Path.cwd())

    # Check if the provided path exists relative to some other path.
    if relative_to is not None:
        relative_to = normalize(relative_to)
        to_check.append(
            relative_to if relative_to.is_dir() else relative_to.parent
        )

    # Return the first file we find on the search path, if we find one.
    for search in to_check:
        search = normalize(search)
        if search.is_dir():
            candidate = search.joinpath(path)
            if candidate.is_file():
                return candidate

    return None
