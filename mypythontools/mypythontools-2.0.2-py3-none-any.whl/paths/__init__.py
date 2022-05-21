"""Some functions around paths. You can find here `find_path()` to find some path efficiently in
some folder, excluding some other inner folders (like venv, node_modules etc.). There is also function
to get desktop path in posix way.
"""

from mypythontools.paths.paths_internal import (
    find_path,
    get_desktop_path,
    isFolderEmpty,
    is_path_free,
    validate_path,
    PathLike,
)

__all__ = ["find_path", "get_desktop_path", "isFolderEmpty", "is_path_free", "validate_path", "PathLike"]
