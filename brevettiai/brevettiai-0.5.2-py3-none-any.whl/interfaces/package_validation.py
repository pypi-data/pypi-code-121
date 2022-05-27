"""
This interface uses "pkg_resources.working_set" to check the validity of the current python installation against
a target list of packages and versions
"""
import pkg_resources
from typing import Dict, List
import toml
import inspect
import os


def installed_packages() -> Dict[str, str]:
    """
    Retrieve 'sorted' dictionary of installed package names and versions

    Returns:

    """
    working_set = sorted(pkg_resources.working_set, key=lambda x: x.project_name)
    return {d.project_name: d.version for d in working_set if not d.project_name.startswith("-")}


def load_packages_from_poetry_lock(path) -> Dict[str, str]:
    """
    Load packages in poetry.lock file

    Args:
        path: path to lock

    Returns:

    """
    lock_file = toml.load(path)
    return {p["name"]: p["version"] for p in lock_file["package"]}


def load_poetry_lock(type_) -> Dict[str, str]:
    """
    Load closest poetry.lock file for an object type

    Args:
        type_: Tyep of object to find lock file for

    Returns:

    """
    source = os.path.dirname(inspect.getfile(type_))
    while source and not os.path.ismount(source):
        try:
            return load_packages_from_poetry_lock(os.path.join(os.path.dirname(source), "poetry.lock"))
        except FileNotFoundError:
            source = os.path.dirname(source)
    raise FileNotFoundError(f"Could not find poetry.lock file above '{os.path.dirname(inspect.getfile(type_))}'")


def get_module_version_status(target_packages: Dict[str, str]) -> Dict[str, List[str]]:
    """Build status of environment compared to a dictionary of target packages"""
    package_info = {"missing": [], "different": [], "extras": [], "ok": []}
    for package, version in installed_packages().items():
        target_version = target_packages.get(package)
        if target_version is None:
            package_info["extras"].append(f"{package}=={version}")
        elif version != target_version:
            package_info["different"].append(f"{package}=={version} should be {target_version}")
        else:
            package_info["ok"].append(f"{package}=={version}")

    return package_info


def get_module_status_from_poetry_lock(type_) -> Dict[str, List[str]]:
    """Retrieve status of environment compared to a poetry.lock definition"""
    target_packages = load_poetry_lock(type_)
    return get_module_version_status(target_packages)


def get_installed_modules() -> List[str]:
    """Retrieve list of installed modules"""
    return list(map("==".join, installed_packages().items()))
