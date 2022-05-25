"""
Tiamat PIP configuration.
"""
import contextlib
import importlib.machinery
import os
import pathlib
import site
import sys
from typing import Optional
from typing import Union


class GlobalContext:
    """
    This class will hold some global runtime context information.
    """

    __slots__ = ("user_base", "user_site", "pip_command_name")

    def __init__(self):
        self.pip_command_name: str = "pip"
        self.user_base: Optional[pathlib.Path] = None
        self.user_site: Optional[pathlib.Path] = None


GLOBAL_CONTEXT = GlobalContext()
if "TIAMAT_PIP_PYPATH" in os.environ:
    GLOBAL_CONTEXT.user_base = pathlib.Path(os.environ["TIAMAT_PIP_PYPATH"]).resolve()
    GLOBAL_CONTEXT.user_site = (
        GLOBAL_CONTEXT.user_base
        / "lib"
        / "python{}.{}".format(*sys.version_info)
        / "site-packages"
    )

if GLOBAL_CONTEXT.user_base is not None:
    site.ENABLE_USER_SITE = True
    site.USER_BASE = str(GLOBAL_CONTEXT.user_base)
    site.USER_SITE = str(GLOBAL_CONTEXT.user_site)


class TiamatPipPathFinder(importlib.machinery.PathFinder):
    """
    Tiamat PIP implementation of python's PathFinder.

    A subclass of PathFinder with the intent to only try and load
    existing modules/packages from the tiamat-pip pypath.

    The reason for this is because pyinstaller specifically pushes PathFinder instances
    to the end of the sys.meta_path list, however, for our hacked pip support to work,
    we need a PathFinder instance before Pyinstaller's pyimod03_importers.FrozenImporter
    """

    path = None

    def __init__(self, path):
        if TiamatPipPathFinder.path is None:
            TiamatPipPathFinder.path = path

    @classmethod
    def _path_importer_cache(cls, path):
        """
        Get the finder for the path entry from sys.path_importer_cache.

        If the path entry is not in the cache, find the appropriate finder
        and cache it. If no finder is available, store None.
        """
        if not path.startswith(str(TiamatPipPathFinder.path)):
            # Don't handle any other paths
            return None
        return super()._path_importer_cache(path)  # type: ignore[misc]

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        """
        Find the spec for a module.
        """
        if path is None:
            assert TiamatPipPathFinder.path
            # First time trying to load
            top_level = fullname.split(".")[0]
            if TiamatPipPathFinder.path.joinpath(top_level).is_dir():
                return super().find_spec(fullname, path=path, target=target)
            if list(TiamatPipPathFinder.path.glob(f"{top_level}.*")):
                return super().find_spec(fullname, path=path, target=target)
        else:
            # Previously loaded, likely the top level package
            for entry in path:
                if entry.startswith(str(TiamatPipPathFinder.path)):
                    return super().find_spec(fullname, path=path, target=target)
        return None


def set_user_base_path(
    user_base: Union[pathlib.Path, str],
    create: bool = True,
    create_mode: int = 0o0755,
) -> None:
    """
    Set the runtime ``user_base`` path.
    """
    if not isinstance(user_base, pathlib.Path):
        user_base = pathlib.Path(user_base)

    user_site = (
        user_base / "lib" / "python{}.{}".format(*sys.version_info) / "site-packages"
    )
    if create is True:
        with contextlib.suppress(PermissionError):
            user_site.mkdir(parents=True, exist_ok=True, mode=create_mode)

    # Make sure our pypath comes first in sys.path
    if str(user_site) in sys.path:
        sys.path.remove(str(user_site))
    sys.path.insert(0, str(user_site))

    GLOBAL_CONTEXT.user_base = user_base
    GLOBAL_CONTEXT.user_site = user_site
    site.ENABLE_USER_SITE = True
    site.USER_BASE = str(user_base)
    site.USER_SITE = str(user_site)

    inject_index = None
    for idx, item in enumerate(sys.meta_path):
        name = getattr(item, "__qualname__", None)
        if name == "TiamatPipPathFinder":
            # our TiamatPipPathFinder is already present, stop processing
            break
        module = getattr(item, "__module__", None)
        if module == "pyimod03_importers":
            # We found Pyinstaller's FrozenImporter, our TiamatPipPathFinder
            # needs to be added in front of it. Store the index.
            inject_index = idx
            break

    if inject_index:
        # Insert our TiamatPipPathFinder before Pyinstaller's FrozenImporter
        sys.meta_path.insert(inject_index, TiamatPipPathFinder(user_site))


def get_user_base_path() -> Optional[pathlib.Path]:
    """
    Get the runtime ``user_base`` path.
    """
    return GLOBAL_CONTEXT.user_base


def get_user_site_path() -> Optional[pathlib.Path]:
    """
    Get the runtime ``user_site`` path.
    """
    return GLOBAL_CONTEXT.user_site


def set_pip_command_name(name: str) -> None:
    """
    Set the runtime ``pip_command_name``.
    """
    GLOBAL_CONTEXT.pip_command_name = name


def get_pip_command_name() -> str:
    """
    Get the runtime ``pip_command_name``.
    """
    return GLOBAL_CONTEXT.pip_command_name
