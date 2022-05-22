# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring
# pylint: disable=too-many-return-statements  # it is fine dear

FORMATTERS = {'True': 'true', 'False': 'false',  'None': 'nil'}


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

    sarg = str(arg)  # cast to str to format it or return sting

    return FORMATTERS.get(sarg, sarg)  # this looks funny :DDDD


def pprint(*args: list) -> None:

    """Overrides stock print() function"""

    print(' '.join(map(wrap, args)))  # white-space' joined str
