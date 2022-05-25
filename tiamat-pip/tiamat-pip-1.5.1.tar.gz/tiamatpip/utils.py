"""
Tiamat pip related utilities.
"""
import logging
import os
import pprint
import sys
from contextlib import contextmanager
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from typing import Sequence

import pip._internal.metadata

from tiamatpip import configure

# Hold a reference to the real function
real_get_default_environment = pip._internal.metadata.get_default_environment

log = logging.getLogger(__name__)


@contextmanager
def patched_environ(
    *, environ: Optional[Dict[str, str]] = None, **kwargs: str
) -> Generator[None, None, None]:
    """
    Context manager to patch ``os.environ``.
    """
    _environ = environ.copy() if environ else {}
    _environ.update(**kwargs)
    old_values = {}
    try:
        for key, value in _environ.items():
            msg_prefix = "Setting"
            if key in os.environ:
                msg_prefix = "Updating"
                old_values[key] = os.environ[key]
            log.debug(f"{msg_prefix} environ variable {key} to: '{value}'")
            os.environ[key] = value
        yield
    finally:
        for key in _environ:
            if key in old_values:
                log.debug(f"Restoring environ variable {key} to: '{old_values[key]}'")
                os.environ[key] = old_values[key]
            else:
                if key in os.environ:
                    log.debug(f"Removing environ variable {key}")
                    os.environ.pop(key)


@contextmanager
def patched_sys_argv(argv: Sequence[str]) -> Generator[None, None, None]:
    """
    Context manager to patch ``sys.argv``.
    """
    previous_sys_argv = list(sys.argv)
    try:
        log.debug(f"Patching sys.argv to: {argv}")
        sys.argv[:] = argv
        yield
    finally:
        log.debug(f"Restoring sys.argv to: {previous_sys_argv}")
        sys.argv[:] = previous_sys_argv


def get_default_environment():
    """
    Get the default environment where packages are installed.
    """
    if "TIAMAT_PIP_UNINSTALL" in os.environ:
        user_base_path = configure.get_user_base_path()
        assert user_base_path
        user_site_path = configure.get_user_site_path()
        assert user_site_path
        return pip._internal.metadata.get_environment(
            paths=[
                str(user_base_path),
                str(user_site_path),
            ],
        )
    return real_get_default_environment()


def patch_pip_internal_metadata_get_default_environment() -> None:
    """
    Patch ``pip._internal.metadata.get_default_environment``.
    """
    pip._internal.metadata.get_default_environment = get_default_environment


@contextmanager
def debug_print(
    funcname: str, argv: List[str], **extra: Any
) -> Generator[None, None, None]:
    """
    Helper debug function.
    """
    prefixes_of_interest = ("TIAMAT_", "LD_", "C_", "CPATH")
    environ = {}
    for key, value in os.environ.items():
        if key.startswith(prefixes_of_interest):
            environ[key] = value
    header = f"Func: {funcname}"
    tail_len = 70 - len(header) - 5
    environ_str = "\n".join(
        f"    {line}" for line in pprint.pformat(environ).splitlines()
    )
    argv_str = "\n".join(f"    {line}" for line in pprint.pformat(argv).splitlines())
    message = (
        f">>> {header} " + ">" * tail_len + "\n"
        f"  CWD: {os.getcwd()}\n"
        f"  ENVIRON:\n{environ_str}\n"
        f"  ARGV:\n{argv_str}\n"
    )
    if extra:
        message += "  EXTRA:\n"
        for key, value in extra.items():
            message += f"    {key}: {value}\n"
    log.debug(message)
    try:
        yield
    finally:
        message = f"<<< {header} " + "<" * tail_len + "\n"
        log.debug(message)
