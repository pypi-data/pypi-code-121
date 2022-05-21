import builtins
from collections.abc import Callable
from collections.abc import Iterator
from contextlib import contextmanager
from functools import partial
from os import getenv
from re import search
from typing import Any
from typing import Optional
from typing import TypeVar

from hypothesis import Verbosity
from hypothesis import assume
from hypothesis import settings
from hypothesis.strategies import SearchStrategy
from hypothesis.strategies import fixed_dictionaries
from hypothesis.strategies import just
from hypothesis.strategies import lists
from hypothesis.strategies import tuples

from dycw_utilities.text import ensure_str
from dycw_utilities.typeguard import typeguard_ignore


@typeguard_ignore
@contextmanager
def assume_does_not_raise(
    *exceptions: type[Exception], match: Optional[str] = None
) -> Iterator[None]:
    """Assume a set of exceptions are not raised. Optionally filter on the
    string representation of the exception.
    """

    try:
        yield
    except exceptions as caught:
        if match is None:
            _ = assume(False)
        else:
            (msg,) = caught.args
            if search(match, ensure_str(msg)):
                _ = assume(False)
            else:
                raise


_TD = TypeVar("_TD")


def draw_and_map(
    func: Callable[..., _TD], *args: Any, **kwargs: Any
) -> SearchStrategy[_TD]:
    """Draw the elements and then pass them into a transformer."""

    return _lift_args_and_kwargs(*args, **kwargs).map(partial(_apply, func))


def draw_and_flatmap(
    func: Callable[..., SearchStrategy[_TD]], *args: Any, **kwargs: Any
) -> SearchStrategy[_TD]:
    """Draw the elements and then flatmap them into a transformer."""

    return _lift_args_and_kwargs(*args, **kwargs).flatmap(partial(_apply, func))


def _lift_args_and_kwargs(
    *args: Any, **kwargs: Any
) -> SearchStrategy[tuple[tuple[Any, ...], dict[str, Any]]]:
    lifted_args = tuples(*map(_lift, args))
    lifted_kwargs = fixed_dictionaries({k: _lift(v) for k, v in kwargs.items()})
    return tuples(lifted_args, lifted_kwargs)


def _lift(x: Any, /) -> SearchStrategy[Any]:
    return x if isinstance(x, SearchStrategy) else just(x)


def _apply(
    func: Callable[..., _TD], x: tuple[tuple[Any, ...], dict[str, Any]], /
) -> _TD:
    args, kwargs = x
    return func(*args, **kwargs)


_TLFL = TypeVar("_TLFL")


def lists_fixed_length(
    strategy: SearchStrategy[_TLFL],
    size: int,
    /,
    *,
    unique: bool = False,
    sorted: bool = False,
) -> SearchStrategy[list[_TLFL]]:
    """Strategy for generating lists of a fixed length."""

    return draw_and_map(
        _draw_lists_fixed_length,
        lists(strategy, min_size=size, max_size=size, unique=unique),
        sorted=sorted,
    )


def _draw_lists_fixed_length(
    elements: list[Any], /, *, sorted: bool = False
) -> list[Any]:
    if sorted:
        return builtins.sorted(elements)
    else:
        return elements


def setup_hypothesis_profiles() -> None:
    """Set up the hypothesis profiles."""

    kwargs = {
        "deadline": None,
        "print_blob": True,
        "report_multiple_bugs": False,
    }
    settings.register_profile("default", max_examples=100, **kwargs)
    settings.register_profile("dev", max_examples=10, **kwargs)
    settings.register_profile("ci", max_examples=1000, **kwargs)
    settings.register_profile(
        "debug", max_examples=10, verbosity=Verbosity.verbose, **kwargs
    )
    settings.load_profile(getenv("HYPOTHESIS_PROFILE", "default"))
