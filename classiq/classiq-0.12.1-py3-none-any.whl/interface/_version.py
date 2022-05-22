import sys

try:
    if sys.version_info >= (3, 8):
        from importlib import metadata
    else:
        import importlib_metadata as metadata
except ImportError:
    raise RuntimeError(
        "Version number unavailable. importlib-metadata is required for Python 3.7"
    )


def package_version(package: str) -> str:
    return metadata.version(package)


try:
    VERSION = package_version("classiq")
except metadata.PackageNotFoundError:
    VERSION = package_version("classiq_interface")
