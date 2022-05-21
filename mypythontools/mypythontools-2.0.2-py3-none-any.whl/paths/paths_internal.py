"""Module with functions for 'paths' subpackage."""

from __future__ import annotations
from typing import Sequence, Union
from pathlib import Path

from ..types import validate_sequence

PathLike = Union[Path, str]  # Path is included in PathLike
"""Str pr pathlib Path. It can be also relative to current working directory."""


def find_path(
    name: str,
    folder: PathLike | None = None,
    exclude_names: Sequence[str] = ("node_modules", "build", "dist"),
    exclude_paths: Sequence[PathLike] = (),
    levels: int = 5,
) -> Path:
    """Search for file or folder in defined folder (cwd() by default) and return it's path.

    Args:
        name (str): Name of folder or file that should be found. If using file, use it with extension
            e.g. "app.py".
        folder (PathLike | None, optional): Where to search. If None, then root is used (cwd by default).
            Defaults to None.
        exclude_names (Sequence[str], optional): List or tuple of ignored names. If this name is whenever in
            path, it will be ignored. Defaults to ('node_modules', 'build', 'dist').
        exclude_paths (Sequence[PathLike], optional): List or tuple of ignored paths. If defined path is
            subpath of found file, it will be ignored. If relative, it has to be from cwd. Defaults to ().
        levels (str, optional): Recursive number of analyzed folders. Defaults to 5.

    Returns:
        Path: Found path.

    Raises:
        FileNotFoundError: If file is not found.
    """
    validate_sequence(exclude_names, "exclude_names")
    validate_sequence(exclude_paths, "exclude_paths")

    folder = Path.cwd() if not folder else validate_path(folder)

    for lev in range(levels):
        glob_file_str = f"{'*/' * lev}{name}"

        for i in folder.glob(glob_file_str):
            is_wanted_file = True
            for j in exclude_names:
                if j in i.parts:
                    is_wanted_file = False
                    break

            if is_wanted_file:
                for j in exclude_paths:
                    excluded_name = Path(j).resolve()
                    if i.as_posix().startswith(excluded_name.as_posix()):
                        is_wanted_file = False
                        break

            if is_wanted_file:
                return i

    # If not returned - not found
    raise FileNotFoundError(f"File `{name}` not found")


def get_desktop_path() -> Path:
    """Get desktop path.

    Returns:
        Path: Return pathlib Path object. If you want string, use `.as_posix()`

    Example:
        >>> desktop_path = get_desktop_path()
        >>> desktop_path.exists()
        True
    """
    return Path.home() / "Desktop"


def validate_path(path: PathLike) -> Path:
    """Convert to pathlib path, resolve to full path and check if exists.

    Args:
        path (PathLike): Validated path.

    Raises:
        FileNotFoundError: If file do not exists.

    Returns:
        Path: Pathlib Path object.

    Example:
        >>> from pathlib import Path
        >>> existing_path = validate_path(Path.cwd())
        >>> non_existing_path = validate_path("not_existing")
        Traceback (most recent call last):
        FileNotFoundError: ...
    """
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"File nor folder found on defined path {path}")
    return path


def isFolderEmpty(path: PathLike) -> bool:
    """Check whether folder is empty.

    Args:
        path (PathLike): Path to folder

    Raises:
        RuntimeError: If there is no folder on path.

    Returns:
        bool: True or False

    Example:
        >>> from pathlib import Path
        >>> from shutil import rmtree
        >>> test_path = Path("isFolderEmptyFolder")
        >>> test_path.mkdir()
        >>> isFolderEmpty(test_path)
        True
        >>> isFolderEmpty(test_path.parent)
        False
        >>> rmtree("isFolderEmptyFolder")
    """
    path = validate_path(path)

    if not path.is_dir():
        raise RuntimeError("On defined path is not folder.")

    content = next(path.iterdir(), None)

    if content is None:
        return True
    else:
        return False


def is_path_free(path: PathLike):
    """Check whether path is available. It means that it doesn't exists yet or its a folder, but it's empty.

    Args:
        path (PathLike): Path to be verified.

    Returns:
        bool: True or False

    Example:
        >>> from pathlib import Path
        >>> from shutil import rmtree
        >>> is_path_free("non/existing/path")
        True
        >>> test_path = Path("isFolderEmptyFolder")
        >>> test_path.mkdir()
        >>> is_path_free(test_path)
        True
        >>> is_path_free(test_path.parent)
        False
        >>> rmtree("isFolderEmptyFolder")
    """
    path = Path(path)
    if not Path(path).exists():
        return True
    else:
        if path.is_dir:
            if isFolderEmpty(path):
                return True
    return False
