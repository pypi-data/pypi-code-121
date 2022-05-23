from typing import Tuple

from nwon_baseline.shell_helper.execute_command import execute_command
from nwon_baseline.typings.version_change import VersionChange


def update_package_version(version_change: VersionChange) -> str:
    version = __new_version(version_change)
    execute_command(["poetry", "version", version])
    return version


def __package_version() -> Tuple[int, int, int]:
    output = "".join(execute_command(["poetry", "version"]))
    version = output.split(" ")[1].split(".")
    return (int(version[0]), int(version[1]), int(version[2]))


def __new_version(version_change: VersionChange) -> str:
    major, minor, patch = __package_version()

    if version_change.value == VersionChange.MAJOR.value:
        major = major + 1

    if version_change.value == VersionChange.MINOR.value:
        minor = minor + 1

    if version_change.value == VersionChange.PATCH.value:
        patch = patch + 1

    return f"{major}.{minor}.{patch}"


__all__ = ["update_package_version"]
