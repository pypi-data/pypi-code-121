import functools
from typing import Callable, Dict, List, Optional

from .session import get_or_create_session
from .utils import get_package_name
from .wrapped_function import WrappedFunction


def metadata(function: Callable[[], Dict[str, str]]):
    """Specify metadata about the session.

    Examples:
        >>> import platform
        >>> import usage
        >>>
        >>> __version__ = "0.27.3"
        >>>
        >>> @usage.metadata
        >>> def get_metadata():
        ...     return {
        ...         "Python": platform.python_version(),
        ...         "OS": platform.system(),
        ...         "Version": __version__
        ...     }

    Raises:
        RuntimeError: If foo
    """
    package = get_package_name(function)
    session = get_or_create_session()
    if package in session.metadata:
        raise RuntimeError

    session.metadata[package] = function()

    return function


def collect(
    function: Optional[Callable] = None,
    *,
    labels: Optional[List[str]] = None,
):
    """Collect usage data from a function.

    Arguments:
        function: The function you want to collect usage data on.
        labels: A list of strings you'd like to label this function with.

    Examples:
        Aasdf

        >>> import usage
        >>>
        >>> @usage.collect(secrets=["token"])
        ... def login(token: str):
        ...     ...

        asdf

        >>> import usage
        >>>
        >>> @usage.collect(labels=["foo"])
        ... def foo():
        ...     ...


    """

    def wrap(function):
        wrapped_function = WrappedFunction(function, labels)

        session = get_or_create_session()
        package = get_package_name(function)
        session.functions[package].add(wrapped_function)

        return functools.wraps(function)(wrapped_function)

    # Allows for both `@usage.collect` and `@usage.collect(...)`.
    if function:
        return wrap(function)

    return wrap
