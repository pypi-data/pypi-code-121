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

>>> from Encodings import *
>>> [encoding for i, encoding in enumerate(get_encodings()) if i > 1]
['utf-8', 'cp1252', 'latin-1']
>>> len(decode_data(bytes(range(256))))
256
>>> urlsafe_b64encode(bytes(range(256)))
b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0-P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn-AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq-wsbKztLW2t7i5uru8vb6_wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t_g4eLj5OXm5-jp6uvs7e7v8PHy8_T19vf4-fr7_P3-_w=='
>>> urlsafe_b64decode(b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0-P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn-AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq-wsbKztLW2t7i5uru8vb6_wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t_g4eLj5OXm5-jp6uvs7e7v8PHy8_T19vf4-fr7_P3-_w==')
b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b\\x0c\\r\\x0e\\x0f\\x10\\x11\\x12\\x13\\x14\\x15\\x16\\x17\\x18\\x19\\x1a\\x1b\\x1c\\x1d\\x1e\\x1f !"#$%&\\'()*+,+./0123456789:;<=\\x0f\\xd0\\x10P\\x90\\xd1\\x11Q\\x91\\xd2\\x12R\\x92\\xd3\\x13S\\x93\\xd4\\x14T\\x94\\xd5\\x15U\\x95\\xd6\\x16V\\x96\\xd7\\x17W\\x97\\xd8\\x18X\\x98\\xd9\\x19Y\\x99\\xda\\x1aZ\\x9a\\xdb\\x1b[\\x9b\\xdc\\x1c\\\\\\x9c\\xdd\\x1d]\\x9d\\xde\\x1e^\\x9e\\xdf\\x1f/\\x9c\\x08\\x18(8HXhx\\x88\\x98\\xa8\\xb8\\xc8\\xd8\\xe8\\xf9\\t\\x19)9IYiy\\x89\\x99\\xa9\\xb9\\xc9\\xd9\\xe9\\xfa\\n\\x1a*:JZjz\\x8a\\x9a\\xaa\\xba\\xca\\xda\\xea\\xc2\\xc6\\xca\\xce\\xd2\\xd6\\xda\\xde\\xe2\\xe6\\xea\\xee\\xf2\\xf6\\xfa\\xc0\\xc1\\xc2\\xc3\\xc4\\xc5\\xc6\\xc7\\xc8\\xc9\\xca\\xcb\\xcc\\xcd\\xce\\xcf\\xd0\\xd1\\xd2\\xd3\\xd4\\xd5\\xd6\\xd7\\xd8\\xd9\\xda\\xdb\\xdc\\xdd\\xde\\xd88x\\xb8\\xf99y\\xb9\\x8e\\x9e\\xae\\xbe\\xce\\xde\\xee\\xff\\x0f\\x1f/\\x13\\xd7\\xdb\\xdf\\xe1\\xfa\\xfb?|'
>>> b64encode(b'abc')
b'YWJj'
>>> b64decode(b'YWJj')
b'abc'
>>> standard_b64encode(b'abc')
b'YWJj'
>>> standard_b64decode(b'YWJj')
b'abc'
>>> b16encode(b'abc')
b'616263'
>>> b16decode(b'616263')
b'abc'
>>> from io import BytesIO
>>> b = BytesIO()
>>> b64encode_file(BytesIO(bytes(range(256))), b)
>>> print(b.getvalue().decode(), end="")
AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4
OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3Bx
cnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmq
q6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj
5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==
>>> b.seek(0)
0
>>> a = BytesIO()
>>> b64decode_file(b, a)
>>> a.getvalue()
b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b\\x0c\\r\\x0e\\x0f\\x10\\x11\\x12\\x13\\x14\\x15\\x16\\x17\\x18\\x19\\x1a\\x1b\\x1c\\x1d\\x1e\\x1f !"#$%&\\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\\x7f\\x80\\x81\\x82\\x83\\x84\\x85\\x86\\x87\\x88\\x89\\x8a\\x8b\\x8c\\x8d\\x8e\\x8f\\x90\\x91\\x92\\x93\\x94\\x95\\x96\\x97\\x98\\x99\\x9a\\x9b\\x9c\\x9d\\x9e\\x9f\\xa0\\xa1\\xa2\\xa3\\xa4\\xa5\\xa6\\xa7\\xa8\\xa9\\xaa\\xab\\xac\\xad\\xae\\xaf\\xb0\\xb1\\xb2\\xb3\\xb4\\xb5\\xb6\\xb7\\xb8\\xb9\\xba\\xbb\\xbc\\xbd\\xbe\\xbf\\xc0\\xc1\\xc2\\xc3\\xc4\\xc5\\xc6\\xc7\\xc8\\xc9\\xca\\xcb\\xcc\\xcd\\xce\\xcf\\xd0\\xd1\\xd2\\xd3\\xd4\\xd5\\xd6\\xd7\\xd8\\xd9\\xda\\xdb\\xdc\\xdd\\xde\\xdf\\xe0\\xe1\\xe2\\xe3\\xe4\\xe5\\xe6\\xe7\\xe8\\xe9\\xea\\xeb\\xec\\xed\\xee\\xef\\xf0\\xf1\\xf2\\xf3\\xf4\\xf5\\xf6\\xf7\\xf8\\xf9\\xfa\\xfb\\xfc\\xfd\\xfe\\xff'
>>> print(b64encode_lines(bytes(range(256))).decode(), end="")
AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4
OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3Bx
cnN0dXZ3eHl6e3x9fn+AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmq
q6ytrq+wsbKztLW2t7i5uru8vb6/wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t/g4eLj
5OXm5+jp6uvs7e7v8PHy8/T19vf4+fr7/P3+/w==
>>> b64decode_lines(b.getvalue())
b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b\\x0c\\r\\x0e\\x0f\\x10\\x11\\x12\\x13\\x14\\x15\\x16\\x17\\x18\\x19\\x1a\\x1b\\x1c\\x1d\\x1e\\x1f !"#$%&\\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\\x7f\\x80\\x81\\x82\\x83\\x84\\x85\\x86\\x87\\x88\\x89\\x8a\\x8b\\x8c\\x8d\\x8e\\x8f\\x90\\x91\\x92\\x93\\x94\\x95\\x96\\x97\\x98\\x99\\x9a\\x9b\\x9c\\x9d\\x9e\\x9f\\xa0\\xa1\\xa2\\xa3\\xa4\\xa5\\xa6\\xa7\\xa8\\xa9\\xaa\\xab\\xac\\xad\\xae\\xaf\\xb0\\xb1\\xb2\\xb3\\xb4\\xb5\\xb6\\xb7\\xb8\\xb9\\xba\\xbb\\xbc\\xbd\\xbe\\xbf\\xc0\\xc1\\xc2\\xc3\\xc4\\xc5\\xc6\\xc7\\xc8\\xc9\\xca\\xcb\\xcc\\xcd\\xce\\xcf\\xd0\\xd1\\xd2\\xd3\\xd4\\xd5\\xd6\\xd7\\xd8\\xd9\\xda\\xdb\\xdc\\xdd\\xde\\xdf\\xe0\\xe1\\xe2\\xe3\\xe4\\xe5\\xe6\\xe7\\xe8\\xe9\\xea\\xeb\\xec\\xed\\xee\\xef\\xf0\\xf1\\xf2\\xf3\\xf4\\xf5\\xf6\\xf7\\xf8\\xf9\\xfa\\xfb\\xfc\\xfd\\xfe\\xff'
>>>

Run tests:
 ~# python -m doctest Encodings.py
 ~# python Encodings.py            # Verbose mode

5 items passed all tests:
  21 tests in __main__
   1 tests in __main__.decode_data
   1 tests in __main__.get_encodings
   1 tests in __main__.urlsafe_b64decode
   1 tests in __main__.urlsafe_b64encode
25 tests in 5 items.
25 passed and 0 failed.
Test passed.

~# coverage run Encodings.py
~# coverage report
Name           Stmts   Miss  Cover
----------------------------------
Encodings.py      54      0   100%
----------------------------------
TOTAL             54      0   100%
~#
"""

__version__ = "0.0.2"
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
    "get_encodings",
    "decode_data",
    "b64encode",
    "b64decode",
    "standard_b64encode",
    "standard_b64decode",
    "b16encode",
    "b16decode",
    "b64encode_file",
    "b64decode_file",
    "b64encode_lines",
    "b64decode_lines",
    "urlsafe_b64encode",
    "urlsafe_b64decode",
]

from binascii import b2a_base64, a2b_base64, unhexlify, hexlify
from base64 import encode, decode, decodebytes, encodebytes
from locale import getpreferredencoding
from contextlib import suppress
from os import device_encoding
from functools import partial


def get_encodings():

    """
    This function returns the probable encodings.

    >>> [encoding for i, encoding in enumerate(get_encodings()) if i > 1]
    ['utf-8', 'cp1252', 'latin-1']
    >>>
    """

    encoding = getpreferredencoding()
    if encoding is not None:
        yield encoding

    encoding = device_encoding(0)
    if encoding is not None:
        yield encoding

    yield "utf-8"  # Default for Linux
    yield "cp1252"  # Default for Windows
    yield "latin-1"  # Can read all files


def decode_data(data: bytes) -> str:

    """
    This function decodes data (try some encodings).

    >>> len(decode_data(bytes(range(256))))
    256
    >>>
    """

    output = None
    for encoding in get_encodings():
        with suppress(UnicodeDecodeError):
            output = data.decode(encoding)
            return output


b64encode = partial(b2a_base64, newline=False)
b64decode = a2b_base64

standard_b64encode = b64encode
standard_b64decode = b64decode

b16encode = hexlify
b16decode = unhexlify

_urlsafe_encode_translation = bytes.maketrans(b"+/", b"-_")
_urlsafe_decode_translation = bytes.maketrans(b"-_", b"+/")

b64encode_file = encode
b64decode_file = decode

b64encode_lines = encodebytes
b64decode_lines = decodebytes


def urlsafe_b64encode(data: bytes) -> bytes:

    """
    Same as base64.urlsafe_b64encode

    >>> urlsafe_b64encode(bytes(range(256)))
    b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0-P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn-AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq-wsbKztLW2t7i5uru8vb6_wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t_g4eLj5OXm5-jp6uvs7e7v8PHy8_T19vf4-fr7_P3-_w=='
    >>>
    """

    return b64encode(data).translate(_urlsafe_encode_translation)


def urlsafe_b64decode(data: bytes) -> bytes:

    """
    Same as base64.urlsafe_b64decode

    >>> urlsafe_b64decode(b'AAECAwQFBgcICQoLDA0ODxAREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0-P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ub3BxcnN0dXZ3eHl6e3x9fn-AgYKDhIWGh4iJiouMjY6PkJGSk5SVlpeYmZqbnJ2en6ChoqOkpaanqKmqq6ytrq-wsbKztLW2t7i5uru8vb6_wMHCw8TFxsfIycrLzM3Oz9DR0tPU1dbX2Nna29zd3t_g4eLj5OXm5-jp6uvs7e7v8PHy8_T19vf4-fr7_P3-_w==')
    b'\\x00\\x01\\x02\\x03\\x04\\x05\\x06\\x07\\x08\\t\\n\\x0b\\x0c\\r\\x0e\\x0f\\x10\\x11\\x12\\x13\\x14\\x15\\x16\\x17\\x18\\x19\\x1a\\x1b\\x1c\\x1d\\x1e\\x1f !"#$%&\\'()*+,+./0123456789:;<=\\x0f\\xd0\\x10P\\x90\\xd1\\x11Q\\x91\\xd2\\x12R\\x92\\xd3\\x13S\\x93\\xd4\\x14T\\x94\\xd5\\x15U\\x95\\xd6\\x16V\\x96\\xd7\\x17W\\x97\\xd8\\x18X\\x98\\xd9\\x19Y\\x99\\xda\\x1aZ\\x9a\\xdb\\x1b[\\x9b\\xdc\\x1c\\\\\\x9c\\xdd\\x1d]\\x9d\\xde\\x1e^\\x9e\\xdf\\x1f/\\x9c\\x08\\x18(8HXhx\\x88\\x98\\xa8\\xb8\\xc8\\xd8\\xe8\\xf9\\t\\x19)9IYiy\\x89\\x99\\xa9\\xb9\\xc9\\xd9\\xe9\\xfa\\n\\x1a*:JZjz\\x8a\\x9a\\xaa\\xba\\xca\\xda\\xea\\xc2\\xc6\\xca\\xce\\xd2\\xd6\\xda\\xde\\xe2\\xe6\\xea\\xee\\xf2\\xf6\\xfa\\xc0\\xc1\\xc2\\xc3\\xc4\\xc5\\xc6\\xc7\\xc8\\xc9\\xca\\xcb\\xcc\\xcd\\xce\\xcf\\xd0\\xd1\\xd2\\xd3\\xd4\\xd5\\xd6\\xd7\\xd8\\xd9\\xda\\xdb\\xdc\\xdd\\xde\\xd88x\\xb8\\xf99y\\xb9\\x8e\\x9e\\xae\\xbe\\xce\\xde\\xee\\xff\\x0f\\x1f/\\x13\\xd7\\xdb\\xdf\\xe1\\xfa\\xfb?|'
    >>>
    """

    return b64decode(data).translate(_urlsafe_decode_translation)


if __name__ == "__main__":
    import doctest

    doctest.testmod(verbose=True)
