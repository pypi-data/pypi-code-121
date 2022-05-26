import datetime

import pkg_resources
from semantic_version import Version


_version = None
_semver = None


def get_version():
    global _version
    if _version:
        return _version

    try:
        _version = pkg_resources.get_distribution("tecton").version
        return _version
    except pkg_resources.DistributionNotFound:
        return None


def get_semantic_version():
    global _semver
    if _semver:
        return _semver

    version = get_version()

    if version is None:
        return None

    _semver = str(Version.coerce(version))
    return _semver


def get_status():
    try:
        from tecton._stamp import BUILD_STATUS

        return BUILD_STATUS
    except ImportError:
        return {}


def get_hash() -> str:
    status = get_status()
    return status.get("GIT_COMMIT", "n/a")


def summary():
    status = get_status()

    ts_seconds = status.get("BUILD_TIMESTAMP", None)
    ts = datetime.datetime.utcfromtimestamp(int(ts_seconds)).isoformat() if ts_seconds else "n/a"

    commit = status.get("GIT_COMMIT", "n/a")

    print(f"Version: {get_version() or 'n/a'}")
    print(f"Git Commit: {commit}")
    print(f"Build Datetime: {ts}")
