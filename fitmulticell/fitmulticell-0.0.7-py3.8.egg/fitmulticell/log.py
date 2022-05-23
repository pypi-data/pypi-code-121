"""Logging utilities."""

import datetime
import platform
import re
import subprocess  # noqa: S404


def _fmc_version():
    from . import __version__

    return __version__


def _pyabc_version():
    import pyabc

    return pyabc.__version__


def _morpheus_version():
    ret = subprocess.run(  # noqa: S607
        ["morpheus", "--version"],
        capture_output=True,
        text=True,
        shell=False,  # noqa: S603
    )
    return re.sub("Version: ", "", ret.stdout.strip())


def _date_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H-%M")


def print_version():
    """Print FitMultiCell, Morpheus, pyABC, Python versions."""
    print(
        f"Running FitMultiCell {_fmc_version()} with "
        f"Morpheus {_morpheus_version()}, pyABC {_pyabc_version()} "
        f"on Python {platform.python_version()} at "
        f"{_date_str()}."
    )
