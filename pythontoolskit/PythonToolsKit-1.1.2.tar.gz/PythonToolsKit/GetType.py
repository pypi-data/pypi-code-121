#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.

>>> import GetType
>>> GetType.try_type("1")
1.0
>>> GetType.try_type("yes")
True
>>> GetType.try_type("null")
>>> GetType.try_type("my string")
'my string'
>>> GetType.get_boolean('true')
True
>>> GetType.get_boolean('FALSE')
False
>>> [i for i in GetType.get_numbers("4.1,5-6.6:0.5")]
[4.1, 5.0, 5.5, 6.0, 6.5]
>>> GetType.is_number("1.1", True)
True
>>> for i in GetType.drange(0.1, 0.5, 0.2): i
...
0.1
0.3
>>>

Run tests:
 ~# python -m doctest GetType.py
 ~# python GetType.py            # Verbose mode

10 items passed all tests:
  10 tests in __main__
   4 tests in __main__.drange
  22 tests in __main__.get_boolean
   4 tests in __main__.get_ips
  14 tests in __main__.get_ipv4_addresses
  15 tests in __main__.get_numbers
   6 tests in __main__.get_step
   9 tests in __main__.is_ip
   5 tests in __main__.is_number
  19 tests in __main__.try_type
108 tests in 10 items.
108 passed and 0 failed.
Test passed.

~# coverage run GetType.py
~# coverage report
Name         Stmts   Miss  Cover
--------------------------------
GetType.py     130      0   100%
--------------------------------
TOTAL          130      0   100%
~#
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = [
    "get_boolean",
    "get_numbers",
    "drange",
    "try_type",
    "is_number",
    "get_ipv4_addresses",
    "is_ip",
]

from ipaddress import ip_address, IPv4Address, IPv4Network
from collections.abc import Iterator
from typing import Any, Tuple
from decimal import Decimal


def get_boolean(
    value: str,
    raise_exception: bool = True,
    default: Any = None,
    case_sensitive: bool = False,
    true_values: Iterator[str] = ("yes", "on", "1", "true", "y"),
    false_values: Iterator[str] = ("no", "off", "0", "false", "n"),
) -> None:

    """
    This function returns a boolean from string value.

    >>> import GetType
    >>> GetType.get_boolean('true')
    True
    >>> GetType.get_boolean('yes')
    True
    >>> GetType.get_boolean('on')
    True
    >>> GetType.get_boolean('1')
    True
    >>> GetType.get_boolean('y')
    True
    >>> GetType.get_boolean('false')
    False
    >>> GetType.get_boolean('off')
    False
    >>> GetType.get_boolean('no')
    False
    >>> GetType.get_boolean('n')
    False
    >>> GetType.get_boolean('0')
    False
    >>> GetType.get_boolean('FALSE')
    False
    >>> GetType.get_boolean('TRUE')
    True
    >>> GetType.get_boolean('+', true_values=['+'], false_values=['-', 'X'])
    True
    >>> GetType.get_boolean('-', true_values=['+'], false_values=['-', 'X'])
    False
    >>> GetType.get_boolean('X', true_values=['+'], false_values=['-', 'X'])
    False
    >>> GetType.get_boolean('x', true_values=['+'], false_values=['-', 'X'])
    False
    >>> try: GetType.get_boolean(
    ...     'invalid',
    ...     true_values=['+'],
    ...     false_values=['-', 'X'],
    ... )
    ... except ValueError: print("ValueError: 'invalid' is not in ['-', 'x', '+']")
    ...
    ValueError: 'invalid' is not in ['-', 'x', '+']
    >>> GetType.get_boolean(
    ...     'invalid',
    ...     true_values=['+'],
    ...     false_values=['-', 'X'],
    ...     raise_exception=False,
    ... )
    >>> GetType.get_boolean(
    ...     'invalid',
    ...     true_values=['+'],
    ...     false_values=['-', 'X'],
    ...     raise_exception=False,
    ...     default="invalid",
    ... )
    'invalid'
    >>> GetType.get_boolean(
    ...     'x',
    ...     true_values=['+'],
    ...     false_values=['-', 'X'],
    ...     raise_exception=False,
    ...     default="invalid",
    ... )
    False
    >>> GetType.get_boolean(
    ...     'x',
    ...     true_values=['+'],
    ...     false_values=['-', 'X'],
    ...     raise_exception=False,
    ...     default="invalid",
    ...     case_sensitive=True,
    ... )
    'invalid'
    >>>
    """

    if not case_sensitive:
        if get_boolean.__defaults__[3] is not true_values:
            true_values = {x.lower() for x in true_values}

        if get_boolean.__defaults__[4] is not false_values:
            false_values = {x.lower() for x in false_values}

        value = value.lower()

    if value in true_values:
        return True
    elif value in false_values:
        return False
    elif raise_exception:
        raise ValueError(
            f"{value!r} is not in {list(false_values) + list(true_values)!r}"
        )
    else:
        return default


def is_number(value: str, raise_exception: bool) -> bool:

    """
    This function checks value for valid number.

    >>> import GetType
    >>> GetType.is_number("1", True)
    True
    >>> GetType.is_number("1.1", True)
    True
    >>> GetType.is_number("abc", True)
    Traceback (most recent call last):
      ...
    ValueError: 'abc' is not a valid number.
    >>> GetType.is_number("abc", False)
    False
    >>>
    """

    integer = value.replace(".", "", 1)

    if integer.isdigit():
        return True
    elif raise_exception:
        raise ValueError(f"{value!r} is not a valid number.")
    else:
        return False


def get_step(
    value: str, step_char: str, step_default: int, raise_exception: bool
) -> Tuple[float, str]:

    """
    This function returns the step value.

    >>> import GetType
    >>> GetType.get_step("0-5:1", ":", 1, True)
    (1.0, '0-5')
    >>> GetType.get_step("0-5?1.1", "?", 1, True)
    (1.1, '0-5')
    >>> GetType.get_step("0-5:abc", ":", 1, True)
    Traceback (most recent call last):
      ...
    ValueError: 'abc' is not a valid number.
    >>> GetType.get_step("0-5:abc", ":", 1, False)
    (1, '0-5')
    >>> GetType.get_step("0-5", ":", 1, True)
    (1, '0-5')
    >>>
    """

    if step_char in value:
        values, step = value.split(step_char, 1)

        if is_number(step, raise_exception):
            return float(step), values
        else:
            return step_default, values
    else:
        return step_default, value


def drange(start: float, stop: float, step: float = 1) -> Iterator[float]:

    """
    This function implements range for Decimal value.

    >>> import GetType
    >>> for i in GetType.drange(0, 5, 2): i
    ...
    0.0
    2.0
    4.0
    >>> for i in GetType.drange(0.1, 0.5, 0.2): i
    ...
    0.1
    0.3
    >>> [i for i in GetType.drange(0, 100, 0.1)][-1]
    99.9
    >>>
    """

    start = Decimal(str(start))
    stop = Decimal(str(stop))
    step = Decimal(str(step))

    x = start

    while x < stop:
        yield float(x)
        x += step


def get_numbers(
    value: str,
    default: Any = None,
    separator: str = ",",
    step_char: str = ":",
    step_default: int = 1,
    generator_char: str = "-",
    raise_exception: bool = True,
) -> Iterator[float]:

    """
    This function yields integers from string value.

    >>> import GetType
    >>> [i for i in GetType.get_numbers("4")]
    [4.0]
    >>> [i for i in GetType.get_numbers("4.1")]
    [4.1]
    >>> [i for i in GetType.get_numbers("4.1,5")]
    [4.1, 5.0]
    >>> [i for i in GetType.get_numbers("4.1,5-7")]
    [4.1, 5.0, 6.0]
    >>> [i for i in GetType.get_numbers("4.1?5-6.6:0.5", separator="?")]
    [4.1, 5.0, 5.5, 6.0, 6.5]
    >>> [i for i in GetType.get_numbers("4.1,5-6.6?invalid", step_char="?")]
    Traceback (most recent call last):
      ...
    ValueError: 'invalid' is not a valid number.
    >>> [i for i in GetType.get_numbers("4.1,invalid?6.6:0.1", generator_char="?")]
    Traceback (most recent call last):
      ...
    ValueError: 'invalid' is not a valid number.
    >>> [i for i in GetType.get_numbers("4.1,??,", generator_char="?")]
    Traceback (most recent call last):
      ...
    ValueError: Generator should be '<float>?<float>:<float>' or '<float>?<float>' or '[float]' (examples: '0?5.5:0.2' '0?5.5' '4') not '??'
    >>> [i for i in GetType.get_numbers("4.1,??,", raise_exception=False)]
    [4.1]
    >>> [i for i in GetType.get_numbers("4.1,??,5.2-5.8:0.2", raise_exception=False)]
    [4.1, 5.2, 5.4, 5.6]
    >>> [i for i in GetType.get_numbers("4.1,??,5.2-5.8:abc", raise_exception=False)]
    [4.1, 5.2]
    >>> [i for i in GetType.get_numbers("4.1,??,5.2-5.8:abc", raise_exception=False, step_default=0.2)]
    [4.1, 5.2, 5.4, 5.6]
    >>> [i for i in GetType.get_numbers("1,?,abc-def,5.2-5.8:abc", raise_exception=False, default=0)]
    [1.0, 0, 0, 5.2]
    >>> [i for i in GetType.get_numbers("5.2-5.8-abc:def", raise_exception=False, default=0)]
    [0]
    >>>
    """

    generators = value.split(separator)

    for generator_ in generators:
        values = generator_.split(generator_char)

        if len(values) == 1:
            value = values.pop()
            if is_number(value, raise_exception):
                yield float(value)
            elif default is not None:
                yield default

        elif len(values) == 2:
            value1, value2 = values
            step, value2 = get_step(
                value2, step_char, step_default, raise_exception
            )

            if is_number(value1, raise_exception) and is_number(
                value2, raise_exception
            ):
                yield from drange(float(value1), float(value2), step)
            elif default is not None:
                yield default

        elif raise_exception:
            raise ValueError(
                f"Generator should be '<float>{generator_char}<float>"
                f"{step_char}<float>' or '<float>{generator_char}<float>' or"
                f" '[float]' (examples: '0{generator_char}5.5{step_char}0.2'"
                f" '0{generator_char}5.5' '4') not {generator_!r}"
            )

        elif default is not None:
            yield default


def try_type(value: str) -> Any:

    """
    This function returns a typed value (be careful with this function,
    detection can be bad (example: if you want a string of number this
    function will return a float)).

    >>> import GetType
    >>> GetType.try_type("1")
    1.0
    >>> GetType.try_type("1.5")
    1.5
    >>> GetType.try_type("yes")
    True
    >>> GetType.try_type("on")
    True
    >>> GetType.try_type("y")
    True
    >>> GetType.try_type("true")
    True
    >>> GetType.try_type("false")
    False
    >>> GetType.try_type("n")
    False
    >>> GetType.try_type("no")
    False
    >>> GetType.try_type("0")
    0.0
    >>> GetType.try_type("")
    >>> GetType.try_type("null")
    >>> GetType.try_type("None")
    >>> GetType.try_type("none")
    >>> GetType.try_type("NULL")
    >>> GetType.try_type("abc")
    'abc'
    >>> GetType.try_type("my string")
    'my string'
    >>> GetType.try_type("Y")
    True
    >>>
    """

    value_ = value.lower()
    boolean = get_boolean(value_, False, case_sensitive=True)

    if is_number(value, False):
        return float(value)
    elif boolean is not None:
        return boolean
    elif not value or value_ == "null" or value_ == "none":
        return None
    else:
        return value


def is_ip(value: str, raise_exception: bool) -> bool:

    """
    This function valids IPv4 addresses.

    >>> import GetType
    >>> GetType.is_ip("0.0.0.0", True)
    True
    >>> GetType.is_ip("255.255.255.255", True)
    True
    >>> GetType.is_ip("255.255.255", True)
    Traceback (most recent call last):
      ...
    ValueError: '255.255.255' is not a valid IPv4 address(should be 4 byte values separate by '.', examples: 0.0.0.0 255.255.255.255)
    >>> GetType.is_ip("255.255.255.256", True)
    Traceback (most recent call last):
      ...
    ValueError: '255.255.255.256' is not a valid IPv4 address ('256' is not a valid byte value).
    >>> GetType.is_ip("255.255.255.abc", True)
    Traceback (most recent call last):
      ...
    ValueError: '255.255.255.abc' is not a valid IPv4 address ('abc' is not a valid byte value).
    >>> GetType.is_ip("255.255.255.01", True)
    Traceback (most recent call last):
      ...
    ValueError: '255.255.255.01' is not a valid IPv4 address ('01' is not a valid byte value).
    >>> GetType.is_ip("255.255.255.01", False)
    False
    >>> GetType.is_ip("255.255.255", False)
    False
    >>>
    """

    numbers = value.split(".")

    if len(numbers) != 4:
        if raise_exception:
            raise ValueError(
                f"{value!r} is not a valid IPv4 address"
                "(should be 4 byte values separate by '"
                ".', examples: 0.0.0.0 255.255.255.255)"
            )
        else:
            return False

    for number in numbers:
        if (
            not number.isdigit()
            or (len(number) > 1 and number.startswith("0"))
            or int(number) > 255
        ):
            if raise_exception:
                raise ValueError(
                    f"{value!r} is not a valid IPv4 address "
                    f"({number!r} is not a valid byte value)."
                )
            else:
                return False

    return True


def get_ips(ip1: ip_address, ip2: ip_address) -> Iterator[ip_address]:

    """
    This function yields IP addresses from first IP to second.

    >>> import GetType
    >>> [str(i) for i in GetType.get_ips(ip_address("10.10.10.0"), ip_address("10.10.10.10"))]
    ['10.10.10.0', '10.10.10.1', '10.10.10.2', '10.10.10.3', '10.10.10.4', '10.10.10.5', '10.10.10.6', '10.10.10.7', '10.10.10.8', '10.10.10.9']
    >>> [str(i) for i in GetType.get_ips(ip_address("10.10.10.10"), ip_address("10.10.10.0"))]
    ['10.10.10.0', '10.10.10.1', '10.10.10.2', '10.10.10.3', '10.10.10.4', '10.10.10.5', '10.10.10.6', '10.10.10.7', '10.10.10.8', '10.10.10.9']
    >>> [str(i) for i in GetType.get_ips(ip_address("::1"), ip_address("::5"))]
    ['::1', '::2', '::3', '::4']
    >>>
    """

    if ip1 > ip2:
        ip1, ip2 = ip2, ip1

    while ip1 < ip2:
        yield ip1
        ip1 += 1


def get_ipv4_addresses(
    value: str,
    default: Any = None,
    separator: str = ",",
    generator_char: str = "-",
    raise_exception: bool = True,
) -> Iterator[IPv4Address]:

    """
    This function yields ip addresses.

    >>> import GetType
    >>> [str(i) for i in GetType.get_ipv4_addresses("10.10.10.10-10.10.10.0")]
    ['10.10.10.0', '10.10.10.1', '10.10.10.2', '10.10.10.3', '10.10.10.4', '10.10.10.5', '10.10.10.6', '10.10.10.7', '10.10.10.8', '10.10.10.9']
    >>> [str(i) for i in GetType.get_ipv4_addresses("10.10.10.0/29")]
    ['10.10.10.1', '10.10.10.2', '10.10.10.3', '10.10.10.4', '10.10.10.5', '10.10.10.6']
    >>> [str(i) for i in GetType.get_ipv4_addresses("10.10.10.0")]
    ['10.10.10.0']
    >>> [str(i) for i in GetType.get_ipv4_addresses("10.10.10.0/33")]
    Traceback (most recent call last):
      ...
    ValueError: '10.10.10.0/33' is not a valid network (example: 127.0.0.1/29) [<valid ip>/<0-32>].
    >>> [str(i) for i in GetType.get_ipv4_addresses("10.10.10.0/abc")]
    Traceback (most recent call last):
      ...
    ValueError: '10.10.10.0/abc' is not a valid network (example: 127.0.0.1/29) [<valid ip>/<0-32>].
    >>> [str(i) for i in GetType.get_ipv4_addresses("10.10.10.0/abc", raise_exception=False)]
    []
    >>> [str(i) for i in GetType.get_ipv4_addresses("10.10.10.0/abc", default="0.0.0.0", raise_exception=False)]
    ['0.0.0.0']
    >>> [str(i) for i in GetType.get_ipv4_addresses("10.10.10.0?10.10.10.2", generator_char="?")]
    ['10.10.10.0', '10.10.10.1']
    >>> [str(i) for i in GetType.get_ipv4_addresses("10.10.10.0/10.10.10.2", generator_char="/")]
    Traceback (most recent call last):
      ...
    ValueError: separator/generator_char should not be '/' (reserved by network)
    >>> [str(i) for i in GetType.get_ipv4_addresses("10.10.10.0/10.10.10.2", separator="/")]
    Traceback (most recent call last):
      ...
    ValueError: separator/generator_char should not be '/' (reserved by network)
    >>> [str(i) for i in GetType.get_ipv4_addresses("abc", default="0.0.0.0", raise_exception=False)]
    ['0.0.0.0']
    >>> [str(i) for i in GetType.get_ipv4_addresses("abc-def", default="0.0.0.0", raise_exception=False)]
    ['0.0.0.0']
    >>> [str(i) for i in GetType.get_ipv4_addresses("127.0.0.1,127.0.0.2")]
    ['127.0.0.1', '127.0.0.2']
    >>>
    """

    if separator == "/" or generator_char == "/":
        raise ValueError(
            "separator/generator_char should not be '/' (reserved by network)"
        )

    ips = value.split(separator)

    for ip in ips:
        if "/" in ip:

            ip_, network = ip.split("/", 1)
            if (
                is_ip(ip_, raise_exception)
                and network.isdigit()
                and 0 <= int(network) <= 32
            ):
                yield from IPv4Network(ip).hosts()
            elif raise_exception:
                raise ValueError(
                    f"{ip!r} is not a valid network (example: 127.0.0.1/29)"
                    " [<valid ip>/<0-32>]."
                )
            elif default is not None:
                yield default

        elif generator_char in ip:

            value1, value2 = ip.split(generator_char, 1)
            if is_ip(value1, raise_exception) or is_ip(
                value2, raise_exception
            ):
                ip1 = IPv4Address(value1)
                ip2 = IPv4Address(value2)
                yield from get_ips(ip1, ip2)
            elif default is not None:
                yield default

        elif is_ip(ip, raise_exception):
            yield IPv4Address(ip)

        elif default is not None:
            yield default


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
