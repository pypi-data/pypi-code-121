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

>>> from Json import invalid_json_example1, invalid_json_example2
>>> from Json import get_valid_json, load_invalid_json
>>> from json import loads
>>> loads(get_valid_json(invalid_json_example1))
{'true': True, 'false': False, 'null': None, '15,45': [15, 45, 15, 45, 15, 45]}
>>> load_invalid_json(invalid_json_example2)
{True: 'true', False: 'false', None: None, '\\n\\tabc\\n\\t': '\\n\\tqwerty\\n\\t', 15.45: 15.45}
>>>

Run tests:
 ~# python -m doctest Json.py
 ~# python Json.py            # Verbose mode

3 items passed all tests:
   5 tests in __main__
   4 tests in __main__.get_valid_json
   4 tests in __main__.load_invalid_json
13 tests in 3 items.
13 passed and 0 failed.
Test passed.

~# coverage run Json.py
~# coverage report
Name      Stmts   Miss  Cover
-----------------------------
Json.py      46      0   100%
-----------------------------
TOTAL        46      0   100%
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

__all__ = ["load_invalid_json", "get_valid_json"]

from re import compile as recompile, I
from ast import literal_eval
from typing import Any

regex_true = recompile(r"([{[,:}\]]\s*)true", I)
regex_false = recompile(r"([{[,:}\]]\s*)false", I)
regex_none = recompile(r"([{[,:}\]]\s*)(null|none|nil)", I)
regex_comma = recompile(r",(\s*[}\]])")
regex_comma_float1 = recompile(
    r'([:{][^["\w\d]*\s*\d+),(\d+\s*[^]"\w\d]*[,:}])'
)
regex_comma_float2 = recompile(
    r'([,:{][^["\w\d]*\s*\d+),(\d+\s*[^]"\w\d]*[:}])'
)
regex_simplequote1 = recompile(r"'(\s*[]{},:[])")
regex_simplequote2 = recompile(r"([]{},:[]\s*)'")

invalid_json_example1 = """{
	'true": True,
	"false': FALSE,
	"null": nil,
	'null': none,
	"15,45": 15,45,
	"15,45": [15,45,15,45,15,45,],
}"""

invalid_json_example2 = """{
	True: 'true',
	FALSE: "false",
	none: nil,
	'''
	abc
	''': \"\"\"
	qwerty
	\"\"\",
	15,45: 15,45,
}"""


def get_valid_json(json: str) -> str:

    """
    This function returns a valid JSON from invalid JSON.

    >>> from Json import invalid_json_example1, invalid_json_example2
    >>> from Json import get_valid_json, load_invalid_json
    >>> from json import loads
    >>> loads(get_valid_json(invalid_json_example1))
    {'true': True, 'false': False, 'null': None, '15,45': [15, 45, 15, 45, 15, 45]}
    >>>
    """

    json = regex_true.sub(r"\g<1>true", json, count=0)
    json = regex_false.sub(r"\g<1>false", json, count=0)
    json = regex_none.sub(r"\g<1>null", json, count=0)
    json = regex_comma.sub(r"\g<1>", json, count=0)
    json = regex_comma_float1.sub(r"\g<1>.\g<2>", json, count=0)
    json = regex_comma_float2.sub(r"\g<1>.\g<2>", json, count=0)
    json = regex_simplequote1.sub(r'"\g<1>', json, count=0)
    json = regex_simplequote2.sub(r'\g<1>"', json, count=0)

    return json


def load_invalid_json(json: str) -> Any:

    """
    This function load invalid JSON.

    >>> from Json import invalid_json_example1, invalid_json_example2
    >>> from Json import get_valid_json, load_invalid_json
    >>> from json import loads
    >>> load_invalid_json(invalid_json_example2)
    {True: 'true', False: 'false', None: None, '\\n\\tabc\\n\\t': '\\n\\tqwerty\\n\\t', 15.45: 15.45}
    >>>
    """

    json = regex_true.sub(r"\g<1>True", json, count=0)
    json = regex_false.sub(r"\g<1>False", json, count=0)
    json = regex_none.sub(r"\g<1>None", json, count=0)
    json = regex_comma_float1.sub(r"\g<1>.\g<2>", json, count=0)
    json = regex_comma_float2.sub(r"\g<1>.\g<2>", json, count=0)

    return literal_eval(json)


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
