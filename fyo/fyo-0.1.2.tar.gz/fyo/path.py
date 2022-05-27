"""Pure syntactic sugar for filesystem tasks."""

from __future__ import annotations

import os
import shutil
import sys

from pathlib import Path as _path_
from pathlib import _posix_flavour  # type: ignore
from pathlib import _windows_flavour  # type: ignore


if sys.version_info.major == 3 and sys.version_info.minor >= 11:
    from typing import Unpack  # type: ignore
else:
    from typing_extensions import Unpack

from typing import TypedDict


class PathListKwargs(TypedDict):
    """Kwargs types for Path class list method."""

    files: bool
    folders: bool
    extension: str
    deep: bool
    begins_with: str
    ends_with: str
    hidden: bool
    recursive: bool


class Path(_path_):
    """Extends the default Pathlib Path class."""

    _flavour = _windows_flavour if os.name == "nt" else _posix_flavour

    def __new__(cls, *args: str) -> Path:
        """Controls the creation of the object."""
        return super(Path, cls).__new__(cls, *args)

    def __init__(self, *args: str) -> None:
        super().__init__()  # Path.__init__ does not take any arg (all is done in new)

    def list(
        self,
        files: bool = True,
        folders: bool = True,
        extension: str = "",
        deep: bool = False,
        begins_with: str = "",
        ends_with: str = "",
        hidden: bool = False,
        recursive: bool = False,
    ) -> list[Path]:
        """
        List and conditionally filter files and/ or folders.

        Parameters
        ----------
        files : bool, optional
            If should list files or not, by default True
        folders : bool, optional
            If should list folders or not, by default True
        extension : str, optional
            Filter by file extension (if file is True), by default ""
        deep : bool, optional
            Also list all immediate subdirectories, by default False
        begins_with : str, optional
            Filter by object name start, by default ""
        ends_with : str, optional
            Filter by object name end, by default ""
        hidden : bool, optional
            If should list hidden files (dot prefix), by default False
        recursive : bool, optional
            Recursively list all subdirectories, by default False

        Returns
        -------
        list[Path]
            Collection of listed Path objects.

        Raises
        ------
        FileNotFoundError
            In case the path does not exist.
        NotADirectoryError
            In case the path is not a directory.
        """
        if not self.exists():
            raise FileNotFoundError(f"'{self}' does not exist")
        elif not self.is_dir():
            raise NotADirectoryError(f"'{self}' is not a directory")

        glob_expr = f"{begins_with}*{ends_with}"

        if recursive:
            glob_expr = f"*/{glob_expr}"
            if deep:
                glob_expr = f"*{glob_expr}"

        objs = list(self.glob(glob_expr))

        if not files:
            objs = [obj for obj in objs if not obj.is_file()]
        elif files and extension != "":
            objs = [obj for obj in objs if obj.suffix == extension]

        if not folders:
            objs = [obj for obj in objs if not obj.is_dir()]
        elif folders and not hidden:
            objs = [obj for obj in objs if not obj.name.startswith(".")]

        # Pylance is highlighting a warning here, for some reason
        return objs  # type: ignore

    def make_archieve(self, target: Path) -> None:
        """
        Pack a file or folder to a target.

        Must be a zip or tar file. Target must be a full path, including the suffix.

        Parameters
        ----------
        target : Path
            Directory of the file or folder to pack.
        """
        nome_zip = str(target.parent / target.stem)
        formato = (target.suffix).replace(".", "")
        diretorio_raiz = self.parent
        diretorio_base = self
        shutil.make_archive(nome_zip, formato, diretorio_raiz, diretorio_base)

    def unpack(self, target: Path) -> None:
        """
        Unpack a compressed file to a target.

        Must be a zip or tar file. Target must be an existing directory.

        Parameters
        ----------
        target : Path
            Where to unpack the compressed package.
        """
        ext = (self.suffix).replace(".", "")
        shutil.unpack_archive(self, target, format=ext)

    def remove(self, **kwargs: Unpack[PathListKwargs]) -> None:
        """
        Delete a file or folder.

        Accepts the same kwargs as list.
        """
        if self.is_file():
            self.unlink()
            return

        for item in self.list(**kwargs):
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    def copy_to(
        self,
        target: Path,
        override: bool = True,
        **kwargs: Unpack[PathListKwargs],
    ) -> None:
        """
        Copy a file or folder to a target.

        Accepts the same kwargs as list.

        Parameters
        ----------
        target : Path
            Copy to this target.
        override : bool, optional
            Replace objects with the same filename, by default True.

        Raises
        ------
        FileExistsError
            In case target already exists and override is False
        """
        for item in self.list(**kwargs):
            if item.is_dir():
                try:
                    shutil.copytree(item, target / item.name)
                except FileExistsError as e:
                    if override:
                        self.remove(**kwargs)
                        self.copy_to(target, False, **kwargs)
                        return
                    raise e
            elif item.is_file():
                shutil.copy(item, target / item.name)
