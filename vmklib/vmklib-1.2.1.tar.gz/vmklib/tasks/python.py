"""
Utilities for working with Python.
"""

# built-in
from os import environ
from pathlib import Path
from platform import system
from sys import version_info


def python_version() -> str:
    """Get the version of Python to use."""
    return environ.get(
        "PYTHON_VERSION", f"{version_info[0]}.{version_info[1]}"
    )


def venv_name(version: str = None) -> str:
    """Get the name for a virtual environment to use."""
    if version is None:
        version = python_version()
    return f"venv{version}"


def venv_dir(cwd: Path, version: str = None) -> Path:
    """Get the path for a virtual environment to use."""
    return cwd.joinpath(venv_name(version))


def venv_bin(cwd: Path, program: str = None, version: str = None) -> Path:
    """Get the path to a virtual environment's script directory."""

    path = venv_dir(cwd, version).joinpath(
        "bin" if not system() == "Windows" else "Scripts"
    )
    if program is not None:
        path = path.joinpath(program)
    return path
