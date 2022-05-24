"""Pythonic wrapper around the excellent `ArkhamDB API <https://arkhamdb.com/api/>`__. Designed to be standalone and importable to other projects."""  # noqa: E501

# uses the version from pyproject.toml via importlib.metadata
# for python versions < 3.7 need to add the backport
# poetry add --python="<3.8" importlib_metadata
try:
    from importlib.metadata import PackageNotFoundError, version  # type: ignore # noqa
except ImportError:  # pragma: no cover # noqa
    from importlib_metadata import PackageNotFoundError, version  # type: ignore # noqa
try:  # noqa
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
