"""
PyInstaller hook for ``tiamatpip``.
"""
import logging
import opcode
import os
import pathlib
import site
from typing import List
from typing import Optional
from typing import Tuple

from distutils.sysconfig import get_python_inc

log = logging.getLogger(__name__)


def get_package_path_from_site_packages_dir(package: str) -> Optional[pathlib.Path]:
    """
    Return a path to the package under ``site-packages``.
    """
    for path in site.getsitepackages():
        resolved_path = pathlib.Path(path).resolve()
        site_packages_dir: pathlib.Path = resolved_path / package
        if site_packages_dir.exists():
            log.info("`site-packages` path for %s: %s", package, site_packages_dir)
            return site_packages_dir
    return None


def get_pip_hidden_imports() -> List[str]:
    """
    Return a list of the pip modules.
    """
    site_packages_path = get_package_path_from_site_packages_dir("pip")
    if not site_packages_path:
        return []
    hidden_imports = set()
    for path in site_packages_path.rglob("*.py"):
        # Get the relative path minus the file extension
        relpath = path.relative_to(site_packages_path).with_suffix("")
        if relpath.name == "__init__":
            # We don't want to consider __init__.py as part of a package name
            relpath = relpath.parent

        # Relative module
        relmod = str(relpath).replace(os.sep, ".")
        if not relmod or relmod == ".":
            continue
        # Real module name
        module = f"{site_packages_path.name}.{relmod}"
        if module.startswith(f"{site_packages_path.name}.tests"):
            # Don't include tests
            continue
        hidden_imports.add(module)
    sorted_hidden_imports = sorted(list(hidden_imports))
    log.info(
        "adding the following pip imports to hidden imports: %s", sorted_hidden_imports
    )
    return sorted_hidden_imports


def get_pip_data_files() -> List[Tuple[str, str]]:
    """
    Return all of pip's files as data files.
    """
    site_packages_path = get_package_path_from_site_packages_dir("pip")
    if not site_packages_path:
        return []
    datas = []
    for fname in site_packages_path.rglob("*"):
        if "__pycache__" in str(fname):
            continue
        if not fname.is_file():
            continue
        if fname.suffix in (".pyc", ".pyo"):
            continue
        relpath = fname.relative_to(site_packages_path.parent)
        datas.append((str(fname), str(relpath.parent)))
    log.info("Including the following pip data files: %s", sorted(datas))
    return datas


def get_distutils_hidden_imports() -> List[str]:
    """
    Collect the distutils hidden imports.
    """
    # The reason why we use optcode to findout about the path of distutils
    # is because on virtualenvs, the real distutils package is not included
    # and it patches python at runtime to the real distutils package.
    # We're using the same approach to find out where the distutils package
    # really is.
    distutils_path = pathlib.Path(opcode.__file__).resolve().parent / "distutils"
    hidden_imports = set()
    for path in distutils_path.rglob("*.py"):
        # Get the relative path minus the file extension
        relpath = path.relative_to(distutils_path).with_suffix("")
        if relpath.name == "__init__":
            # We don't want to consider __init__.py as part of a package name
            relpath = relpath.parent

        # Relative module
        relmod = str(relpath).replace(os.sep, ".")
        if not relmod or relmod == ".":
            continue
        # Real module name
        module = f"{distutils_path.name}.{relmod}"
        if module.startswith(f"{distutils_path.name}.tests"):
            # Don't include tests
            continue
        hidden_imports.add(module)
    sorted_hidden_imports = sorted(list(hidden_imports))
    log.info(
        "adding the following distutils imports to hidden imports: %s",
        sorted_hidden_imports,
    )
    return sorted_hidden_imports


def get_python_header_files() -> List[Tuple[str, str]]:
    """
    Collect the python headers.
    """
    python_include_path = pathlib.Path(get_python_inc())
    datas = []
    for fname in python_include_path.rglob("*.h"):
        relpath = fname.relative_to(python_include_path)
        incpath = pathlib.Path("include") / "python" / relpath
        datas.append((str(fname), str(incpath.parent)))
    log.info("Including the following python header files: %s", sorted(datas))
    return datas


hiddenimports = get_pip_hidden_imports() + get_distutils_hidden_imports()
datas = get_python_header_files() + get_pip_data_files()
