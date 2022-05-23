import functools
import warnings

from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .http import ArgusAPISession


def _load_cli_settings() -> dict:
    """Get argus-cli settings from its configuration file.

    We have to be able to load these settings for backward compatibility,
    """
    try:
        from argus_cli.settings import settings
    except ImportError:
        settings = {}
    return settings


def deprecated_alias(alias_name: str) -> Callable:
    """Decorate a function to raise a deprecation warning before being called.

    This is meant to be used as follows :

    .. code-block: python

       alias = deprecated_alias("alias")(decorated_function)

    The warning will indicate that ``alias_name`` is an alias and that
    ``decorated_function`` is the new name that should be used.

    :param alias_name: name of the alias for the decorated function.
    """

    def deco(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{alias_name} is a deprecated alias for {f.__name__}"
                f"and will be removed; use {f.__name__} instead.",
                DeprecationWarning,
            )
            return f(*args, **kwargs)

        return wrapper

    return deco


def deprecated_module_alias(
    alias_name: str, old_module: str, new_module: str
) -> Callable:
    """Decorate a function to raise a deprecation warning before being called.

    This decorator is to be used when a function has been moved to a different module,
    whether its name has changed or not.

    This is meant to be used as follows :

    .. code-block: python

       alias = deprecated_module_alias("alias", old_module, new_module)(decorated_function)

    The warning will indicate that ``old_module.alias_name`` is an alias and that
    ``new_module.decorated_function`` is the new name that should be used.

    :param alias_name: name of the alias for the decorated function.
    :param old_module: deprecated module import path (ex: "argus_api.lib.service.old_module")
    :param new_module: current module import path (ex: "argus_api.lib.service.current_module")
    """

    def deco(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            warnings.warn(
                f"{old_module}.{alias_name} is a deprecated alias for {new_module}.{f.__name__}"
                f"and will be removed; use {new_module}.{f.__name__} instead.",
                DeprecationWarning,
            )
            return f(*args, **kwargs)

        return wrapper

    return deco
