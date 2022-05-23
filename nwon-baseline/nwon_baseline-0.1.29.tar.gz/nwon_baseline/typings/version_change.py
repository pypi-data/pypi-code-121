from enum import Enum


class VersionChange(Enum):
    MINOR = "minor"
    MAJOR = "major"
    PATCH = "patch"


__all__ = ["VersionChange"]
