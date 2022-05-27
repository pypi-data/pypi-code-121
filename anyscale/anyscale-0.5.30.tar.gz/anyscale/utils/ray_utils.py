# type: ignore
"""
This file contains internal APIs extracted from opensource ray.
"""
import logging
from pathlib import Path
from typing import Callable, List, Optional
from zipfile import ZipFile

from pathspec import PathSpec


default_logger = logging.getLogger(__name__)


"""
The following functions are extracted from: ray._private.runtime_env.packaging
"""

# If an individual file is beyond this size, print a warning.
FILE_SIZE_WARNING = 100 * 1024 * 1024  # 100 MiB


def _mib_string(num_bytes: float) -> str:
    size_mib = float(num_bytes / 1024 ** 2)
    return f"{size_mib:.2f}MiB"


def _get_gitignore(path: Path) -> Optional[Callable]:
    path = path.absolute()
    ignore_file = path / ".gitignore"
    if ignore_file.is_file():
        with ignore_file.open("r") as f:
            pathspec = PathSpec.from_lines("gitwildmatch", f.readlines())

        def match(p: Path):
            path_str = str(p.absolute().relative_to(path))
            return pathspec.match_file(path_str)

        return match
    else:
        return None


def _dir_travel(
    path: Path,
    excludes: List[Callable],
    handler: Callable,
    logger: Optional[logging.Logger] = default_logger,
):
    """Travels the path recursively, calling the handler on each subpath.
    Respects excludes, which will be called to check if this path is skipped.
    """
    e = _get_gitignore(path)

    if e is not None:
        excludes.append(e)
    skip = any(e(path) for e in excludes)
    if not skip:
        try:
            handler(path)
        except Exception as e:
            logger.error(f"Issue with path: {path}")
            raise e
        if path.is_dir():
            for sub_path in path.iterdir():
                _dir_travel(sub_path, excludes, handler, logger=logger)

    if e is not None:
        excludes.pop()


def _get_excludes(path: Path, excludes: List[str]) -> Callable:
    path = path.absolute()
    pathspec = PathSpec.from_lines("gitwildmatch", excludes)

    def match(p: Path):
        path_str = str(p.absolute().relative_to(path))
        return pathspec.match_file(path_str)

    return match


def zip_directory(
    directory: str,
    excludes: List[str],
    output_path: str,
    include_parent_dir: bool = False,
    logger: Optional[logging.Logger] = default_logger,
) -> None:
    """Zip the target directory and write it to the output_path.
    directory (str): The directory to zip.
    excludes (List(str)): The directories or file to be excluded.
    output_path (str): The output path for the zip file.
    include_parent_dir: If true, includes the top-level directory as a
        directory inside the zip file.
    """
    pkg_file = Path(output_path).absolute()
    with ZipFile(pkg_file, "w") as zip_handler:
        # Put all files in the directory into the zip file.
        dir_path = Path(directory).absolute()

        def handler(path: Path):
            # Pack this path if it's an empty directory or it's a file.
            if path.is_dir() and next(path.iterdir(), None) is None or path.is_file():
                file_size = path.stat().st_size
                if file_size >= FILE_SIZE_WARNING:
                    logger.warning(
                        f"File {path} is very large "
                        f"({_mib_string(file_size)}). Consider adding this "
                        "file to the 'excludes' list to skip uploading it: "
                        f"runtime_env={{'excludes': ['{path}', ...], ...}}`"
                    )
                to_path = path.relative_to(dir_path)
                if include_parent_dir:
                    to_path = dir_path.name / to_path
                zip_handler.write(path, to_path)

        excludes = [_get_excludes(dir_path, excludes)]
        _dir_travel(dir_path, excludes, handler, logger=logger)
