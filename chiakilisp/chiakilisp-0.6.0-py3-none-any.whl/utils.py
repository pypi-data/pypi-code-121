# pylint: disable=invalid-name
# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-return-statements  # it is fine dear

from typing import Callable, Iterable

FORMATTERS = {'True': 'true', 'False': 'false',  'None': 'nil'}


def get_assertion_closure(e_object) -> Callable:

    """Returns the 'ASSERT()' function for the 'e_object'"""

    def ASSERT(t_pos: str, condition, *args) -> None:
        """Helps to raise custom exception when asserting"""

        if not condition:
            msg, *rst = args
            raise e_object(
                f'{t_pos} {e_object.__name__}: {msg}', *rst)

    return ASSERT  # <---- thus, return an assertion closure


def wrap(arg) -> str:

    """Wraps any Python 3 value (safely) into string"""

    if isinstance(arg, str):  # if it's a str(), wrap it in '"'
        return f'"{arg}"'

    if callable(arg):  # if it's an object (function and class)

        if hasattr(arg, 'x__custom_name__x'):
            return arg.x__custom_name__x  # <--- that simple :D

        return str(getattr(
            arg, '__name__',
            getattr(arg, '__class__', None).__name__)  # <- >_<
        )

    if isinstance(arg, list):  # wrap each child of the list()

        formatted = ' '.join(map(wrap, arg))
        return f'[{formatted}]'

    if isinstance(arg, tuple):  # handle tuple()'s as list()'s

        formatted = ' '.join(map(wrap, arg))
        return f'({formatted})'

    if isinstance(arg, dict):  # special handling for dict()'s

        formatted = ' '.join(map(
            lambda _pair: f'{wrap(_pair[0])} {wrap(_pair[1])}',
            arg.items())
        )
        return f'{{{formatted}}}'

    if arg is ...:
        return '...'  # <---- print ...  for Ellipsis instances

    sarg = str(arg)  # cast to str to format it or return sting

    return FORMATTERS.get(sarg, sarg)  # this looks funny :DDDD


def pprint(*args: list) -> None:

    """Overrides stock print() function"""

    print(' '.join(map(wrap, args)))  # white-space' joined str


def simple_fuzzy_matched(item: str, glossary: Iterable) -> tuple:

    """This returns most fuzzy matched strings in the glossary"""

    scored = tuple(map(
        lambda possible: (len(set(possible) - set(item)), possible),
        glossary
    ))  # <- returns something like ((1, 'foo'), 2, 'bar') and so on

    lowest = min(tuple(map(
        lambda pair: pair[0],
        filter(
            lambda pair: pair[0] != 0,  # skip over 0 scored results
            scored
        )
    )))  # <----- returns the most lower score in the `scored` tuple

    return tuple(filter(
        lambda candidate: (
                len(candidate) - len(item) >= 5  # <-- tune it later
                or len(item) - len(candidate) <= 5   # tune it later
        ),
        map(
            lambda pair: pair[1],
            filter(lambda pair: pair[0] == lowest, scored)
        )
    ))  # <--- returns a tuple of candidates with the `lowest` score
