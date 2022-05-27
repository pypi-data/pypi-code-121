import os
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from typing import Any

import jpype
import scyjava

try:
    __version__ = version("bioformats_jar")
except PackageNotFoundError:
    __version__ = "uninstalled"


__all__ = [
    "get_loci",
    "set_loci_log_level",
    "get_ome",
    "loci",
    "ome",
    "__version__",
]


BIOFORMATS_VERSION = os.getenv("BIOFORMATS_VERSION", "LATEST")
BIOFORMATS_LICENSE = os.getenv("BIOFORMATS_LICENSE", "gpl")
assert BIOFORMATS_LICENSE in {
    "gpl",
    "bsd",
}, "BIOFORMATS_LICENSE env var must be either 'gpl' or 'bsd'"
LOG_LEVEL = os.getenv("BIOFORMATS_LOG_LEVEL", "ERROR")

scyjava.config.endpoints.append(
    f"ome:formats-{BIOFORMATS_LICENSE}:{BIOFORMATS_VERSION}"
)


@lru_cache()
def get_loci(log_level: str = LOG_LEVEL):
    """Start JVM (if necessary) and get the `loci` module

    Parameters
    ----------
    log_level : str
        the logging level for loci tools.  by default "ERROR". Can also be set by
        setting the 'BIOFORMATS_LOG_LEVEL' environment variable.

    Returns
    -------
    loci
        the loci module from bioformats_package.jar
    """
    FormatTools = scyjava.jimport("loci.formats.FormatTools")
    loci = jpype.JPackage("loci")
    loci.common.DebugTools.setRootLevel(log_level)
    loci.__version__ = FormatTools.VERSION
    return loci


def set_loci_log_level(level):
    """Set loging level for loci tools."""
    get_loci().common.DebugTools.setRootLevel(level)


@lru_cache()
def get_ome():
    """Start JVM (if necessary) and get the `ome` module"""
    scyjava.start_jvm()
    return jpype.JPackage("ome")


def __getattr__(name: str) -> Any:
    if name == "loci":
        return get_loci()
    if name == "ome":
        return get_ome()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
