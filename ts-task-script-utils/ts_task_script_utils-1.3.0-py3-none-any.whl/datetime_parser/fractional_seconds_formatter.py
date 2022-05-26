# pylint: skip-file
from pendulum.formatting import Formatter


class FractionalSecondsFormatter(Formatter):
    """`FractionalSecondsFormatter` override microseconds token in _PARSE_TOKENS
    `pendulum.formatting.Formatter`So that, Formatter.parse() will match and
    return dict with microsecond as string. This allow us to catch fractional
    seconds of any number of digits such as '000123000' with leading and trailing
    zeros intact as microseconds.
    """

    _PARSE_TOKENS = {
        "YYYY": lambda year: int(year),
        "YY": lambda year: int(year),
        "Q": lambda quarter: int(quarter),
        "MMMM": lambda month: month,
        "MMM": lambda month: month,
        "MM": lambda month: int(month),
        "M": lambda month: int(month),
        "DDDD": lambda day: int(day),
        "DDD": lambda day: int(day),
        "DD": lambda day: int(day),
        "D": lambda day: int(day),
        "dddd": lambda weekday: weekday,
        "ddd": lambda weekday: weekday,
        "dd": lambda weekday: weekday,
        "d": lambda weekday: int(weekday) % 7,
        "E": lambda weekday: int(weekday),
        "HH": lambda hour: int(hour),
        "H": lambda hour: int(hour),
        "hh": lambda hour: int(hour),
        "h": lambda hour: int(hour),
        "mm": lambda minute: int(minute),
        "m": lambda minute: int(minute),
        "ss": lambda second: int(second),
        "s": lambda second: int(second),
        "S": lambda us: str(us),
        "SS": lambda us: str(us),
        "SSS": lambda us: str(us),
        "SSSS": lambda us: str(us),
        "SSSSS": lambda us: str(us),
        "SSSSSS": lambda us: str(us),
        "a": lambda meridiem: meridiem,
        "X": lambda ts: float(ts),
        "x": lambda ts: float(ts) / 1e3,
        "ZZ": str,
        "Z": str,
        "z": str,
    }
