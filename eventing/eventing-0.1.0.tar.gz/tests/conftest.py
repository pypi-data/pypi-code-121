import importlib
import inspect
from typing import Any, get_args, get_origin, Union
from unittest.mock import Mock

import pytest

import eventing


# Since we're testing a package which keeps a global state across imports
# we need to reload it to remove previous state at the start of each test
# to avoid the side effects. This feels preferable than a fixture doing
# the import; this way is much less boilerplate and the tests better show
# the intended use of the package
def pytest_runtest_setup(item):
    importlib.reload(eventing)


def create_mock_for_parameter(p: inspect.Parameter) -> Any:
    if p.default is not p.empty:
        # we have a default, use it
        return p.default

    if p.kind is p.VAR_POSITIONAL:
        return ()

    if p.kind is p.VAR_KEYWORD:
        return {}

    if p.annotation is p.empty:
        # we have no annotation to go off of, just give it a plain mock
        return Mock()

    origin = get_origin(p.annotation)
    if origin is None and p.annotation:
        # Annotation is probably just a regular type or class
        return Mock(p.annotation)
    elif origin is Union:
        return Mock(get_args(p.annotation)[0])
    else:  # last resort
        return Mock()


@pytest.fixture
def auto_bind_func_with_mocks_from_signature():
    def wrapper(func, /):
        def _auto_bind_func_with_mocks_from_signature(**arg_overrides):
            """Tries to mock a call to the function.

            The function signature will be inspected and all arguments not
            provided by `arg_overrides` will be substituted with a Mock that
            is the best attempt to match the type. Default values are left as
            default. If a type is a Union, the first type in it will be
            provided.

            Args:
                **arg_overrides:
                    argument overrides provided in a keyword fashion. These
                    will be correctly substituted in the function, even if
                    positional only.

            Returns:
                Whatever `func` returns.
            """
            sig = inspect.signature(func)
            args, kwargs = [], {}
            for p in sig.parameters.values():
                try:
                    # we have and override, use it
                    arg = arg_overrides[p.name]
                except KeyError:
                    # try to create a mock that would pass as the argument
                    arg = create_mock_for_parameter(p)

                if p.kind in [p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD]:
                    args.append(arg)
                elif p.kind == p.VAR_POSITIONAL:
                    args.extend(arg)
                elif p.kind == p.KEYWORD_ONLY:
                    kwargs[p.name] = arg
                elif p.kind == p.VAR_KEYWORD:
                    kwargs.update(arg)
                else:
                    raise ValueError("Unknown parameter kind encountered.")

            return func(*args, **kwargs)

        return _auto_bind_func_with_mocks_from_signature

    return wrapper
