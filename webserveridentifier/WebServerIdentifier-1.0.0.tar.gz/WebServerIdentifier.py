#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package identifies web servers.
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
This package identifies Web servers using an aggressive
technique based on the maximum size of the URI.

~# python3 WebServerIdentifier.py -d -v -m HEAD identify 127.0.0.1

PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.


WebServerIdentifier  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.

[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:1133} Command line arguments parsed.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:1150} Identifier built.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:789} New connection built.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:798} URI size: 12276.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} Request 1 sent. Get response...
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:918} Request size: 12278, response status: 400.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:623} Trying to identify server from response hash (sha512).
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:634} Response hash does not match. (sha512: cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e)
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:638} Trying to identify server from response content.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:951} Servers size: 16.
[*] Response status: 400 for request size: 12278.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:789} New connection built.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:798} URI size: 6114.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} Request 2 sent. Get response...
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:918} Request size: 6116, response status: 404.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:951} Servers size: 8.
[*] Response status: 404 for request size: 6116.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:789} New connection built.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:798} URI size: 12218.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} Request 3 sent. Get response...
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:918} Request size: 12220, response status: 400.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:951} Servers size: 4.
[*] Response status: 400 for request size: 12220.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:789} New connection built.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:798} URI size: 9171.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} Request 4 sent. Get response...
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:918} Request size: 9173, response status: 404.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:951} Servers size: 2.
[*] Response status: 404 for request size: 9173.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:789} New connection built.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:798} URI size: 12211.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} Request 5 sent. Get response...
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:918} Request size: 12213, response status: 400.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:951} Servers size: 1.
[*] Response status: 400 for request size: 12213.
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:969} Identifying the Web Server...
[2016-06-22 02:11:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:980} Only one server (IIS) matching with max URI size: 12212
[*] Response status: 400 for request size: 12213.
[+] Server header: 'Microsoft-HTTPAPI/2.0', last request size: 12213, last error code: 400, server(s): 'IIS'.

~# python3 WebServerIdentifier.py -i 1 identify 127.0.0.1:8080

PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.


WebServerIdentifier  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.

[+] Server header: 'SimpleHTTP/0.6 Python/3.10.4', last request size: 61391, last error code: 414, server(s): 'Python'.

~# python3 WebServerIdentifier.py -d -v -m HEAD -i 1 getmaxuri 127.0.0.1

PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.


WebServerIdentifier  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.

[2016-06-22 02:15:36] DEBUG    (10) {__main__ - WebServerIdentifier.py:1138} Command line arguments parsed.
[2016-06-22 02:15:36] DEBUG    (10) {__main__ - WebServerIdentifier.py:1155} Identifier built.
[2016-06-22 02:15:36] DEBUG    (10) {__main__ - WebServerIdentifier.py:831} Get minimum and maximum server URI sizes.
[2016-06-22 02:15:36] DEBUG    (10) {__main__ - WebServerIdentifier.py:852} Start the search for maximum URI length...
[2016-06-22 02:15:36] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:36] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 395735.
[2016-06-22 02:15:36] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 1 sent. Get response...
[2016-06-22 02:15:36] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 395737, response status: 414
[*] Request size: 395737, response code: 414 'Request-URI Too Long'
[2016-06-22 02:15:37] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:37] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 198874.
[2016-06-22 02:15:37] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 2 sent. Get response...
[2016-06-22 02:15:37] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 198876, response status: 414
[*] Request size: 198876, response code: 414 'Request-URI Too Long'
[2016-06-22 02:15:38] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:38] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 100443.
[2016-06-22 02:15:38] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 3 sent. Get response...
[2016-06-22 02:15:38] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 100445, response status: 414
[*] Request size: 100445, response code: 414 'Request-URI Too Long'
[2016-06-22 02:15:39] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:39] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 51228.
[2016-06-22 02:15:39] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 4 sent. Get response...
[2016-06-22 02:15:39] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 51230, response status: 414
[*] Request size: 51230, response code: 414 'Request-URI Too Long'
[2016-06-22 02:15:40] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:40] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 26621.
[2016-06-22 02:15:40] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 5 sent. Get response...
[2016-06-22 02:15:40] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 26623, response status: 414
[*] Request size: 26623, response code: 414 'Request-URI Too Long'
[2016-06-22 02:15:41] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:41] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 14317.
[2016-06-22 02:15:41] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 6 sent. Get response...
[2016-06-22 02:15:41] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 14319, response status: 414
[*] Request size: 14319, response code: 414 'Request-URI Too Long'
[2016-06-22 02:15:42] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:42] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 8165.
[2016-06-22 02:15:42] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 7 sent. Get response...
[2016-06-22 02:15:42] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 8167, response status: 404
[*] Request size: 8167, response code: 404 'Not Found'
[2016-06-22 02:15:43] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:43] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 11241.
[2016-06-22 02:15:43] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 8 sent. Get response...
[2016-06-22 02:15:43] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 11243, response status: 404
[*] Request size: 11243, response code: 404 'Not Found'
[2016-06-22 02:15:44] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:44] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12779.
[2016-06-22 02:15:44] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 9 sent. Get response...
[2016-06-22 02:15:44] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12781, response status: 414
[*] Request size: 12781, response code: 414 'Request-URI Too Long'
[2016-06-22 02:15:45] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:45] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12010.
[2016-06-22 02:15:45] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 10 sent. Get response...
[2016-06-22 02:15:45] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12012, response status: 404
[*] Request size: 12012, response code: 404 'Not Found'
[2016-06-22 02:15:46] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:46] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12394.
[2016-06-22 02:15:46] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 11 sent. Get response...
[2016-06-22 02:15:46] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12396, response status: 414
[*] Request size: 12396, response code: 414 'Request-URI Too Long'
[2016-06-22 02:15:47] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:47] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12202.
[2016-06-22 02:15:47] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 12 sent. Get response...
[2016-06-22 02:15:47] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12204, response status: 404
[*] Request size: 12204, response code: 404 'Not Found'
[2016-06-22 02:15:48] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:48] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12298.
[2016-06-22 02:15:48] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 13 sent. Get response...
[2016-06-22 02:15:48] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12300, response status: 414
[*] Request size: 12300, response code: 414 'Request-URI Too Long'
[2016-06-22 02:15:49] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:49] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12250.
[2016-06-22 02:15:49] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 14 sent. Get response...
[2016-06-22 02:15:49] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12252, response status: 400
[*] Request size: 12252, response code: 400 'Bad Request'
[2016-06-22 02:15:50] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:50] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12226.
[2016-06-22 02:15:50] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 15 sent. Get response...
[2016-06-22 02:15:50] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12228, response status: 400
[*] Request size: 12228, response code: 400 'Bad Request'
[2016-06-22 02:15:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12214.
[2016-06-22 02:15:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 16 sent. Get response...
[2016-06-22 02:15:51] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12216, response status: 400
[*] Request size: 12216, response code: 400 'Bad Request'
[2016-06-22 02:15:52] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:52] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12208.
[2016-06-22 02:15:52] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 17 sent. Get response...
[2016-06-22 02:15:52] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12210, response status: 404
[*] Request size: 12210, response code: 404 'Not Found'
[2016-06-22 02:15:53] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:53] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12211.
[2016-06-22 02:15:53] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 18 sent. Get response...
[2016-06-22 02:15:53] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12213, response status: 400
[*] Request size: 12213, response code: 400 'Bad Request'
[2016-06-22 02:15:54] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:54] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12210.
[2016-06-22 02:15:54] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 19 sent. Get response...
[2016-06-22 02:15:54] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12212, response status: 404
[*] Request size: 12212, response code: 404 'Not Found'
[2016-06-22 02:15:55] DEBUG    (10) {__main__ - WebServerIdentifier.py:794} New connection built.
[2016-06-22 02:15:55] DEBUG    (10) {__main__ - WebServerIdentifier.py:803} URI size: 12211.
[2016-06-22 02:15:55] DEBUG    (10) {__main__ - WebServerIdentifier.py:808} Request 20 sent. Get response...
[2016-06-22 02:15:55] DEBUG    (10) {__main__ - WebServerIdentifier.py:871} Request size: 12213, response status: 400
[*] Request size: 12213, response code: 400 'Bad Request'
[2016-06-22 02:15:55] INFO     (20) {__main__ - WebServerIdentifier.py:882} Maximum URI length found: 12212, status: 400, reason: Bad Request.
[*] Request size: 12212, response code: 400 'Bad Request'
[+] Server header: 'Microsoft-HTTPAPI/2.0'
[+] Maximum URI length is: 12212, error code: 400 'Bad Request'

~#

>>> from WebServerIdentifier import WebServerIdentifier, _create_unverified_context

PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.


WebServerIdentifier  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.

>>> identifier = WebServerIdentifier("127.0.0.1", baseuri="/", ssl=True, context=_create_unverified_context(), port=8000, interval=0.5, timeout=2)
>>> identifier = WebServerIdentifier("127.0.0.1")
>>> response = identifier.request()
>>> response.status
404
>>> response.reason
'Not Found'
>>> r = identifier.request(method="HEAD", size=65535)
>>> r.status
414
>>> r.reason
'Request-URI Too Long'
>>> for size, r in identifier.get_max_URI_size(): pass
...
>>> size
12212
>>> for size, r in identifier.get_max_URI_size(method="HEAD"): pass
...
>>> for r, size, servers in identifier.identify_server(): pass
...
>>> for r, size, servers in identifier.identify_server(method="HEAD"): pass
...
>>> size
12213
>>> servers
{'IIS'}
>>> name = servers.pop()
>>> size
12213
>>> name
'IIS'
>>>

~# python3 -m doctest -v WebServerIdentifier.py
1 items passed all tests:
  19 tests in WebServerIdentifier
19 tests in 20 items.
19 passed and 0 failed.
Test passed.
~#
"""

__version__ = "1.0.0"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package identifies Web servers using an aggressive
technique based on the maximum size of the URI.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/WebServerIdentifier"

copyright = """
WebServerIdentifier  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["WebServerIdentifier"]

from http.client import HTTPConnection, HTTPSConnection, HTTPResponse
from PythonToolsKit.Arguments import ArgumentParser, verbose
from collections.abc import Iterable, Callable, Generator
from PythonToolsKit.Random import get_random_strings
from PythonToolsKit.Logs import get_custom_logger
from typing import Tuple, Set, List, Dict, Union
from ssl import _create_unverified_context
from PythonToolsKit.PrintF import printf
from collections import defaultdict
from dataclasses import dataclass
from argparse import Namespace
from statistics import median
from functools import partial
from operator import lt, ge
from socket import timeout
from logging import Logger
from hashlib import sha512
from time import sleep

import http.client as httpclient

httpclient._MAXLINE = httpclient._MAXLINE * 2

IIS_414_hash: bytes = (
    b"}R8\x95^.\xdf\xb9\xd7b\xc2\xb2\xd21\x91"
    b"\x9aV\x04w\xe0\xbf\xbeu\x90\xa5\xdb\xed\x89"
    b"\xf4\xef\x15\xee\x97\xdbWi\x89\x7f6\xa4\xb4"
    b"`q\xb3~\xbe\x18U\xeb\xd6\x8f\xe8\xcc\x0f\xfe"
    b'\xddy\xd7\x0fq"\xa0\x9a\x84'
)  # md5 b'\x13\xf3\x9b\xc2`\x83c\xe2\x08\xba\x94\x94\xd5\xd67\x9c'

IIS_414_content: bytes = (
    b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01/'
    b'/EN""http://www.w3.org/TR/html4/strict.dtd">\r'
    b"\n<HTML><HEAD><TITLE>Request URL Too Long</TITLE>"
    b'\r\n<META HTTP-EQUIV="Content-Type" Content="text/html;'
    b' charset=us-ascii"></HEAD>\r\n<BODY><h2>Request URL'
    b" Too Long</h2>\r\n<hr><p>HTTP Error 414. The request"
    b" URL is too long.</p>\r\n</BODY></HTML>\r\n"
)

IIS_400_hash: bytes = (
    b"A\x8bR\xbfp\xe4\x13\xe6\xc5\x0b\x0c\xb7\xc5"
    b"\x8dW\x82\x1dW\x01\xe6\xe0\xed\xe3h\xd4-\x94"
    b"@O&Ht{\x89\xd7{\xcf\x99\x18\x8a\xee@j\xc5rh"
    b'\xa7\x12\xcaS\x98n\x8e\xb8\xdb"V\xfa\xb7\xac\x95\x84b\xd4'
)  # md5 b'\x93\xb1uH\xf8\xf2:\xd8\xa30`\xf7\x06\xba\xca\x1d'

IIS_400_content: bytes = (
    b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01/'
    b'/EN""http://www.w3.org/TR/html4/strict.dtd">\r'
    b"\n<HTML><HEAD><TITLE>Bad Request</TITLE>\r\n<META"
    b' HTTP-EQUIV="Content-Type" Content="text/html; '
    b'charset=us-ascii"></HEAD>\r\n<BODY><h2>Bad Request'
    b" - Invalid URL</h2>\r\n<hr><p>HTTP Error 400. The"
    b" request URL is invalid.</p>\r\n</BODY></HTML>\r\n"
)

IIS_400_hash2: bytes = (
    b"\x06\xd8\xfe\x8f\x9c\xaf\x1de\x1d\xf6\xce\xd50\xa7\x0c\xcbg\xf5\xa8"
    b"\x0c\xbc\xf6\xad/\t\x04\xe4\x98!uU\xb3\x13\x0e(\x821J\x00\xfep1\xc8uF"
    b"\x1fL[EGe\xc7N\x8c\xd5\xacC\xe5\xde\xe9\xa7\x12\x14\xf4"
)  # md5 b'\xc7\xf1;\x90\xb0s\x17\x8b@\x91\x02,c[3\x7f'

IIS_400_content2: bytes = (
    b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN""'
    b'http://www.w3.org/TR/html4/strict.dtd">\r\n<HTML>'
    b"<HEAD><TITLE>Bad Request</TITLE>\r\n<META HTTP-EQUIV"
    b'="Content-Type" Content="text/html; charset=us-ascii">'
    b"</HEAD>\r\n<BODY><h2>Bad Request - Request Too Long</h2>"
    b"\r\n<hr><p>HTTP Error 400. The size of the request headers"
    b" is too long.</p>\r\n</BODY></HTML>\r\n"
)

APACHE_hash: bytes = (
    b"\x9f\x9e\x8e\x99i$\xeb\xc5R\x86\xb2\xef6\x7fb\t\x8a"
    b"\xc6\x8c;+\xfa3\x83\x97,\x7f\xcb\x15\xd1\x93n\xfc\r"
    b"\x98K\xaeF\xe3\xc9+j!\x1e\xb9\x9e\xb1\x01\xc3\xfa\x10"
    b"\xfc_\x91\xb3\xac\tha`\xac%.G"
)  # md5 b'\x1c\xfd\xd9M\x9e<\xc8L-;\xaa,\x10W<:'

APACHE_content: bytes = (
    b'<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">\n'
    b"<html><head>\n<title>414 Request-URI Too Long</title>"
    b"\n</head><body>\n<h1>Request-URI Too Long</h1>\n<p>"
    b"The requested URL's length exceeds the capacity\nlimit "
    b"for this server.<br />\n</p>\n<hr>\n<address>Apache/"
)

NGINX_hash: bytes = (
    b"^gf ;\x1f\\\xbe\xe0\x9c\r\x07{0\xba\x82\x91\x94\xfc("
    b"\xf53\xc9\xde\t\x8e\xa4\xfb\xdb\x16\xa5\x15a8<\x1aY"
    b"\x89\xf9,\xc8\xd8&\xc0\xb7\x85\x0f\t|C\xa4\x98\xb0O"
    b'\xe4\xfb\n\x97\xaf\xfc_"P\xc8'
)  # md5 b'\xd2\x1f\x19\xbfq\x7f\xe3\xc8\xde\xce\xb1E\x8b\xdfI\xe9'

NGINX_content: bytes = (
    b"<html>\r\n<head><title>414 Request-URI Too Large</title>"
    b"</head>\r\n<body>\r\n<center><h1>414 Request-URI Too Large"
    b"</h1></center>\r\n<hr><center>nginx/"
)

TOMCAT_hash: bytes = (
    b"\xa80\xcc\x99\x8d1m\xe2\xba\x1d(\xb4\xfd[b\xb8O\xc6\xac\x15"
    b"\xec\x90\xd6c\x8di\xc44o\x93l6I\xff\x1b\x8cV\x1d`5o\xe1\xda"
    b"D\xbf\xc3Bu\xccwh\xa8\xb9\x03\xe8\x90\xb8nI|\n\xb9\x15\xbe"
)  # b'\x06\xc8`\x12\xc2\xec\xdc\x0f\xf5K7[\xbd\x9c*\xa2'

TOMCAT_content: bytes = (
    b'<!doctype html><html lang="en"><head><title>HTTP Status 400'
    b' \xe2\x80\x93 Bad Request</title><style type="text/css">body'
    b" {font-family:Tahoma,Arial,sans-serif;} h1, h2, h3, b {color:"
    b"white;background-color:#525D76;} h1 {font-size:22px;} h2 {font"
    b"-size:16px;} h3 {font-size:14px;} p {font-size:12px;} a {color:"
    b"black;} .line {height:1px;background-color:#525D76;border:none;}"
    b"</style></head><body><h1>HTTP Status 400 \xe2\x80\x93 Bad Request"
    b'</h1><hr class="line" /><p><b>Type</b> Exception Report</p><p><b>'
    b"Message</b> Request header is too large</p><p><b>Description</b>"
    b" The server cannot or will not process the request due to something"
    b" that is perceived to be a client error (e.g., malformed request "
    b"syntax, invalid request message framing, or deceptive request routing)"
    b".</p><p><b>Exception</b>"
)

LIGHTTPD_hash: bytes = (
    b"\xe0\x99\x18\xd7\\\xdeB\xa2M)l\x06\xbc\xfa&\n#\x1e\xf1-\xb3"
    b"k\x92\x04T\xae\x98pw\xbf\xba<\xdb\x1a\xd9\x85Eo\nFa\xc5\x8e"
    b"\xc2\xf8YZ\xba\xb7\x07p#\xfb\xc4\xf4u\x97g\x90\xf9k`M\xd2"
)  # md5 b'-\x8b\x0c\xf9\xbd1m(\xb8f\x0b\x1ah\x97\xce\x8c'

LIGHTTPD_content: bytes = (
    b'<?xml version="1.0" encoding="iso-8859-1"?>\n<!DOCTYPE html PUBLIC'
    b' "-//W3C//DTD XHTML 1.0 Transitional//EN"\n         "http://www.w3'
    b'.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n<html xmlns="http://'
    b'www.w3.org/1999/xhtml" xml:lang="en" lang="en">\n <head>\n  <title>'
    b"431 Request Header Fields Too Large</title>\n </head>\n <body>\n  "
    b"<h1>431 Request Header Fields Too Large</h1>\n </body>\n</html>\n"
)

LITE_SPEED_hash: bytes = (
    b"\xd81U\xbd\x99u\x8c\x85\xdb\xa6\xcf\xd3Xa\x0b"
    b"M \x19\xae\x12r\\\t\xbe\xe1\xb65\xaa\xff\x9fb"
    b"\x89\r\x93A}\x8c\xaa\x84y\xa4\x03\x8c\xdf\xa2"
    b"\x82m\x9byz\x04\x0f\x08j\x88J\xc4\xb2\xa6"
    b"\x18\x88\xe5\xc6\xe1"
)  # md5 b'\x989Q\xf6\x9c\xa9\xeeU\x8b\xcc\xe8\x90\xa6\xbd\x8a\x0e'

LITE_SPEED_content: bytes = (
    b'<!DOCTYPE html>\n<html style="height:100%">\n<head>'
    b'\n<meta name="viewport" content="width=device-width,'
    b' initial-scale=1, shrink-to-fit=no">\n<title> 414 '
    b"Request-URI Too Large\r\n</title></head>\n<body style="
    b'"color: #444; margin:0;font: normal 14px/20px Arial,'
    b" Helvetica, sans-serif; height:100%; background-color:"
    b' #fff;">\n<div style="height:auto; min-height:100%; ">'
    b'     <div style="text-align: center; width:800px; margin'
    b'-left: -400px; position:absolute; top: 30%; left:50%;">\n'
    b'        <h1 style="margin:0; font-size:150px; line-height'
    b':150px; font-weight:bold;">414</h1>\n<h2 style="margin-top'
    b':20px;font-size: 30px;">Request-URI Too Large\r\n</h2>\n<p>'
    b"The request URL is over the maximum size allowed!</p>\n</div>"
    b"</div></body></html>\n"
)

PYTHON_hash: bytes = (
    b"j(a\\\x97 \\V\xb1\xc27\x0e\x9bB\x13\xc4\x81YX\xb8\x805/+/\xea"
    b"\xef\x02\xd4\r\x9a2\xa5\x1e\xe6T\x1aC[\x07\x9f u\xaf\x1c\xbb:K"
    b"\\\x18\x86\xc8\xc1\x03\xe1(rC\xdc\x85>\x89J\xf3"
)  # md5 b'\x8d|p\x8a\tH\xe2 \x1e\t\x89\xd9\x1f\xd2b\xa7'

PYTHON_content: bytes = (
    b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"\n        '
    b'"http://www.w3.org/TR/html4/strict.dtd">\n<html>\n    <head>'
    b'\n        <meta http-equiv="Content-Type" content="text/html'
    b';charset=utf-8">\n        <title>Error response</title>\n    '
    b"</head>\n    <body>\n        <h1>Error response</h1>\n       "
    b" <p>Error code: 414</p>\n        <p>Message: Request-URI Too "
    b"Long.</p>\n        <p>Error code explanation: HTTPStatus.REQU"
    b"EST_URI_TOO_LONG - URI is too long.</p>\n    </body>\n</html>\n"
)

QUARK_hash: bytes = (
    b"\xd8\x83\x0ecAP17Z\x8b\x97\xe4\x81\xfe6\xcf\xfb\x01V\xb6h\x1a"
    b"\xf9p8\xe6\x17\x04\x8b\x88\xb5\x18\x95\xac\x13\x9f#\x8a\x0bd"
    b"\x81Z\n7\xed`x\x06\x915|\xec+}\x18r\x89\xdfX\x9d\xa20>$"
)  # md5 b'a\xba^j\x9c\x97*n\xf9y\x93\xc9\x1c@\xa1\x91'

QUARK_content: bytes = (
    b"<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<title>431 Request Header"
    b" Fields Too Large</title>\n\t</head>\n\t<body>\n\t\t<h1>431 "
    b"Request Header Fields Too Large</h1>\n\t</body>\n</html>\n"
)

TWISTED_hash: bytes = (
    b"\xcf\x83\xe15~\xef\xb8\xbd\xf1T(P\xd6m\x80\x07\xd6 \xe4\x05"
    b"\x0bW\x15\xdc\x83\xf4\xa9!\xd3l\xe9\xceG\xd0\xd1<]\x85\xf2\xb0"
    b"\xff\x83\x18\xd2\x87~\xec/c\xb91\xbdGAz\x81\xa582z\xf9'\xda>"
)  # md5 b'\xd4\x1d\x8c\xd9\x8f\x00\xb2\x04\xe9\x80\t\x98\xec\xf8B~'

TWISTED_content: bytes = b""

RUBY_content: bytes = (
    b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN">\n<HTML>\n'
    b"  <HEAD><TITLE>Request-URI Too Large</TITLE></HEAD>\n  <BODY>\n"
    b"    <H1>Request-URI Too Large</H1>\n    WEBrick::HTTPStatus::"
    b"RequestURITooLarge\n    <HR>\n    <ADDRESS>\n     WEBrick/"
)

RUBY_hash: bytes = (
    b"\x98\xae\xf9\xcf\xfaw\xc1\xebH\xf5qBl\x86A9\xac\xb4\xc0/\xa4"
    b'\xe6\x1b\xab\xc6\x1e\x08\xf0\xda<\xcf"\xda}\xca\xbfG\xc8\xa9W'
    b"\xbc2\x8d\x13\xf9w+\xd4\xc0\xf3\x93\xe8\xc0\xf9\xf6n\xea\x9d"
    b"\xd1R\xa8\x93}\xcb"
)  # md5 b'Rd\xfeg\xfb\xe9\xff\x93\x03\xc5\x1c\xdd\xbbj\xf1I'

PERLM_hash: bytes = (
    b"\xa0y\xd5\xa3UB\x16\xaa\x18L\x80\xb7~\xb6\x08\xea}\xe05g\x15"
    b"\xdd@)\x17\x97q\xc5\xb8R\xdc\x1b\xa4G \x85\xbd\x04i9\xacm\x9b"
    b"\x1bc\x8bX\x9b\x86\x07\x96rj.)\xe2 \x0f\x0fb\x14\xc3\xdb\xa3"
)  # md5 b'i\xf7L\xe9\xa8Uk`\xd4\xc9EEC<\x17\xb1'

PERLM_content: bytes = (
    b'<meta http-equiv="Pragma" content="no-cache">\n    <meta http'
    b'-equiv="Expires" content="-1">\n    <script src="/mojo/jquery/'
    b'jquery.js"></script>\n    <script src="/mojo/highlight.js/high'
    b'light.min.js"></script>\n    <script src="/mojo/highlight.js/'
    b'mojolicious.min.js"></script>\n    <script src="/mojo/bootstrap'
    b'/bootstrap.js"></script>\n    <link href="/mojo/bootstrap/'
    b'bootstrap.css" rel="stylesheet">\n    <link href="/mojo/highlight'
    b'.js/highlight-mojo-dark.css" rel="stylesheet">\n    <link href='
    b'"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/'
)

NODEJS_hash: bytes = (
    b"\xcf\x83\xe15~\xef\xb8\xbd\xf1T(P\xd6m\x80\x07\xd6 \xe4\x05\x0b"
    b"W\x15\xdc\x83\xf4\xa9!\xd3l\xe9\xceG\xd0\xd1<]\x85\xf2\xb0\xff"
    b"\x83\x18\xd2\x87~\xec/c\xb91\xbdGAz\x81\xa582z\xf9'\xda>"
)  # md5 b'\xd4\x1d\x8c\xd9\x8f\x00\xb2\x04\xe9\x80\t\x98\xec\xf8B~'

NODEJS_content: bytes = b""

ERLANG_hash: bytes = (
    b"\x85d\xfa\xba\xd3+j\xae\xc8\xaa\x05|\x8b\xbb\x198\xee\xaf\x00+\xd8"
    b"\x93I\xfd\xc2\xebJ\xdf\xc0\xae\x0e\xab0\xc3\xc7\x9dQvz8\xf0\\\x8fL"
    b"\xa4 \xc3;\xbb\x1f\xfb\xc7{\xfb\xdc\xfd\x92\xd6\x82\xad|f\x16\xf1"
)  # md5 b';g\xc2\r\xca/\x11\x14[\x97\x8d\x8e}\xe6si'

ERLANG_content: bytes = (
    b"<HTML>\n       <HEAD>\n           <TITLE>Internal Server Error"
    b"</TITLE>\n      </HEAD>\n      <BODY>\n      <H1>Internal Server"
    b" Error</H1>\nThe server encountered an internal error or "
    b"misconfiguration and was unable to complete your request.<P>Please"
    b" contact the server administrator"
)

WEBFS_hash: bytes = (
    b"\xfb\x1e\xf6(\x07\xc7c0\xa3\xdc\xd2\xc1\xbe\xce\xd5&\xa6\xe3>\xf0^\xda"
    b"\xbe\x93\xdb\xc4\xa0\x95\xe3\xd3\xb1\x7f\xc8w\x1a\n\x18\x19\x0f\x81"
    b"\xe83\x04!\xe2/\xf4\x89\x08 \xa7\xb0x\xc9+\x86`}5\xfe\x12\xb9\xa2\xd1"
)  # md5 b'\xaa\xa9(\xb3:\xb7\xd1\x1b#\x91\xe9\xa1*e\xbe`'

WEBFS_content: bytes = b"*PLONK*\n"

TRAEFIK_hash: bytes = (
    b"\xd8\xd09s-\xbf\xa4\x14\xb8iE#3\xb9\x89_9BB\xa2SE\x0cm\x82\xa1S\x0c\x15"
    b"\xed=$\xbe\x95\xf5\x1d\xabX?vV\xdc\x05\x90\xd0\xb0\xac\xb8\xf0B\x93\xea"
    b"\x80\x13\x13\xc4\xd1\x87a2\xe0\xc7O\xaa"
)  # md5 b'\x85\xef\x13\x10[v\x8c\xc9\xe3\x18:\xb8Z\xb9J\xc9'

TRAEFIK_content: bytes = b"431 Request Header Fields Too Large"

H2O_hash: bytes = (
    b"\xbf\xe6\xe8\xdf6\xc7\x8c\xbf\xd1{\xa9'\x0c\x86\x86\x0e\xe9\xb0Q\xb8%"
    b"\x94\xfb\x8f4\xa0\xad\xf6\xa1N\x15\x96\xd2\xa9\xdc\xdc~\xb6\x85q\x01\xe1"
    b"P*\xffo\xf5\x15\xa3n\x8b\xa6\xc8\r\xa3'\xbc\x11\x83\x16$\xa5\xda\xea"
)  # md5 b'\x82VD\xf7G\xba\xab,\x00\xe4 \xdb\xbc9\xe4\xb3'

H2O_content: bytes = b"Bad Request"

CADDY_hash: bytes = (
    b"\xd8\xd09s-\xbf\xa4\x14\xb8iE#3\xb9\x89_9BB\xa2SE\x0cm\x82\xa1S\x0c\x15"
    b"\xed=$\xbe\x95\xf5\x1d\xabX?vV\xdc\x05\x90\xd0\xb0\xac\xb8\xf0B\x93\xea"
    b"\x80\x13\x13\xc4\xd1\x87a2\xe0\xc7O\xaa"
)  # md5 b'\x85\xef\x13\x10[v\x8c\xc9\xe3\x18:\xb8Z\xb9J\xc9'

CADDY_content: bytes = b"431 Request Header Fields Too Large"


class MaxURIerror:

    """
    This class groups the max URI error attributes
    and place it in class attributes for research.
    """

    hashes = defaultdict(set)
    contents = defaultdict(set)
    status = defaultdict(set)
    min_sizes = defaultdict(set)

    def __init__(
        self,
        server: str,
        min_size: int = None,
        code: int = None,
        hash_: str = None,
        countains: bytes = None,
    ):
        self.server: str = server
        self.min_size: int = min_size
        self.code: int = code
        self.hash: str = hash_
        self.countains = countains

        if hash_ is not None:
            MaxURIerror.hashes[hash_].add(server)

        if code is not None:
            MaxURIerror.status[code].add(server)

        if countains is not None:
            MaxURIerror.contents[countains].add(server)

        if min_size is not None:
            MaxURIerror.min_sizes[min_size].add(server)

    @staticmethod
    def content_identification(data: bytes) -> Tuple[str, Union[str, None]]:

        """
        This function returns a server name
        if the response match.
        """

        logger_debug("Trying to identify server from response hash (sha512).")
        hash_ = sha512(data).digest()
        servers = MaxURIerror.hashes.get(hash_)

        if servers is not None:
            logger_info(
                "Response hash match with "
                f"{', '.join(servers)!r} ! (sha512: {hash_.hex()})"
            )
            return servers
        else:
            logger_debug(
                f"Response hash does not match. (sha512: {hash_.hex()})"
            )

        logger_debug("Trying to identify server from response content.")
        for content, servers in MaxURIerror.contents.items():
            if len(content) < 55:
                if data == content:
                    logger_info(
                        "Response hash match with "
                        f"{''.join(servers)!r} ! (content: {content!r})"
                    )
                    return servers
            else:
                if content in data:
                    logger_info(
                        "Response hash match with "
                        f"{''.join(servers)!r} ! (content: {content!r})"
                    )
                    return servers


servers: Dict[str, List[MaxURIerror]] = {
    "IIS": [
        MaxURIerror("IIS", 12284, 414, IIS_414_hash, IIS_414_content),
        MaxURIerror("IIS", 12241, 400, IIS_400_hash, IIS_400_content),
        MaxURIerror("IIS", 12212, 400, IIS_400_hash2, IIS_400_content2),
    ],
    "Python": [MaxURIerror("Python", 49140, 414, PYTHON_hash, PYTHON_content)],
    "Apache": [MaxURIerror("Apache", 6134, 414, APACHE_hash, APACHE_content)],
    "NGINX": [MaxURIerror("NGINX", 6133, 414, NGINX_hash, NGINX_content)],
    "Lighttp": [
        MaxURIerror("Lighttp", 6095, 431, LIGHTTPD_hash, LIGHTTPD_content),
        MaxURIerror("Lighttp", 6066, 431),
    ],
    "OpenLiteSpeed": [
        MaxURIerror(
            "OpenLiteSpeed", 24577, 414, LITE_SPEED_hash, LITE_SPEED_content
        ),
        MaxURIerror("OpenLiteSpeed", 16164, 503),
        MaxURIerror("OpenLiteSpeed", 16164, 0),
    ],
    "Caddy": [
        MaxURIerror("Caddy", 52175, 431),
        MaxURIerror("Caddy", 52145, 431, CADDY_hash, CADDY_content),
    ],
    "Tomcat": [
        MaxURIerror("Tomcat", 6092, 400),
        MaxURIerror("Tomcat", 6062, 400, TOMCAT_hash, TOMCAT_content),
        MaxURIerror("Tomcat", 6092, 0),
    ],
    "Traefik": [
        MaxURIerror("Traefik", 789458, 431),
        MaxURIerror("Traefik", 789422, 431),
        MaxURIerror("Traefik", 789426, 431),
        MaxURIerror("Traefik", 789428, 431, TRAEFIK_hash, TRAEFIK_content),
    ],
    "WitchServer": [MaxURIerror("WitchServer", None, 0)],  # 49070
    "Cherokee": [
        MaxURIerror("Cherokee", 6098, 413),
        MaxURIerror("Cherokee", 6066, 0),
        MaxURIerror("Cherokee", 6063, 0),
    ],
    "H2O": [
        MaxURIerror("H2O", 313294, 400),
        MaxURIerror("H2O", 313262, 400, H2O_hash, H2O_content),
    ],
    "Quark": [MaxURIerror("Quark", 2015, 431, QUARK_hash, QUARK_content)],
    "Twisted": [
        MaxURIerror("Twisted", 12245, 400),
        MaxURIerror("Twisted", 12214, 400),
        MaxURIerror("Twisted", 12278, 0),
    ],
    "Ruby": [MaxURIerror("Ruby", 2015, 414, RUBY_hash, RUBY_content)],
    "PerlMojolicious": [
        MaxURIerror("PerlMojolicious", 2015, 500, PERLM_hash, PERLM_content)
    ],
    "PerlPlack": [
        MaxURIerror("PerlPlack", 98256, 0),
        MaxURIerror("PerlPlack", 98222, 0),
    ],
    "NodeJS": [
        MaxURIerror("NodeJS", 12257, 431),
        MaxURIerror("NodeJS", 12227, 431),
    ],
    "Php": [MaxURIerror("Php", 61391, 0), MaxURIerror("Php", 61358, 0)],
    "Erlang": [MaxURIerror("Erlang", 2015, 500, ERLANG_hash, ERLANG_content)],
    "Busybox": [MaxURIerror("Busybox", None, None)],
    "Webfs": [
        MaxURIerror("Webfs", 2015, 400, WEBFS_hash, WEBFS_content),
        MaxURIerror("Webfs", 2990, 0),
    ],
}


@dataclass
class CustomResponse:
    status: int
    reason: str

    def read(self) -> bytes:

        """
        Compatibility with HTTPResponse.
        """

        return b""


class WebServerIdentifier:

    """
    This class implements the Web Server Identifier.

    target: The target host (examples: "10.101.10.101:8000", "example.com")
    ssl:    Use HTTPS (SSL, Encryption)
    """

    def __init__(
        self,
        target: str,
        baseuri: str = "/",
        ssl: bool = False,
        interval: float = 0,
        user_agent: str = "WebServerIdentifier " + __version__,
        *args,
        **kwargs,
    ):
        self.max_size: int = None
        self.target: str = target
        self.request_counter: int = 0
        self.error_status: int = None
        self.error_reason: str = None
        self.interval: float = interval
        self.last_response: HTTPResponse = None
        self.baseuri: str = baseuri if baseuri[-1] == "/" else (baseuri + "/")
        self.headers = {"User-Agent": user_agent}
        self.connection_class: Callable = (
            partial(HTTPSConnection, target, *args, **kwargs)
            if ssl
            else partial(HTTPConnection, target, *args, **kwargs)
        )

        self.baseuri_length = len(baseuri)

    def request(self, method: str = "GET", size: int = 0) -> HTTPResponse:

        """
        This function requests the Web Server.

        method: HTTP method to use
        size:   Size of the Query String
        """

        connection = self.connection_class()
        logger_debug("New connection built.")

        uri = self.baseuri
        size = size - self.baseuri_length - 1
        if size > 0:
            uri += "?" + get_random_strings(size, urlsafe=True)
        else:
            size = 0

        logger_debug(f"URI size: {size}.")

        try:
            connection.request(method, uri, headers=self.headers)
            self.request_counter += 1
            logger_debug(
                f"Request {self.request_counter} sent. Get response..."
            )
            response = connection.getresponse()
        except (
            ConnectionRefusedError,
            ConnectionResetError,
            TimeoutError,
            timeout,
        ) as e:
            response = CustomResponse(0, e.__class__.__name__)
            logger_debug("Connection error.")

        return response

    @staticmethod
    def get_min_and_max() -> Tuple[int, int]:

        """
        This function returns the minimum and maximum
        size to get a "too long URI error".
        """

        logger_debug("Get minimum and maximum server URI sizes.")
        sizes = MaxURIerror.min_sizes
        return min(sizes), max(sizes)

    def get_max_URI_size(
        self, *args, **kwargs
    ) -> Generator[Tuple[int, HTTPResponse]]:

        """
        This function detects the max URI length of the target.
        """

        error_codes: Dict[int, Set[str]] = MaxURIerror.status
        min_, max_ = self.get_min_and_max()
        interval: int = self.interval
        status: int = 0
        diff: int = 0

        error_status: int = None
        error_reason: str = None

        logger_debug("Start the search for maximum URI length...")

        while diff != 1:
            if interval and diff:
                sleep(interval)

            diff = round((max_ - min_) / 2) or 1
            size = min_ + diff

            response = self.request(*args, size=size, **kwargs)

            status = response.status
            if status in error_codes:
                max_ = size
                error_status = status
                error_reason = response.reason
            else:
                min_ = size

            logger_debug(f"Request size: {size}, response status: {status}")
            yield size, response

        if status in error_codes:
            size = size - 1

        self.max_size = size
        self.last_response = response
        self.error_status = error_status
        self.error_reason = error_reason

        logger_info(
            f"Maximum URI length found: {size}, status: "
            f"{error_status}, reason: {error_reason}."
        )

        yield size, response

    def identify_server(
        self, *args, **kwargs
    ) -> Generator[HTTPResponse, int, Dict[int, str], Iterable[str]]:

        """
        This function identifies the target's web server.
        """

        maxsize_servers: Dict[int, Set[str]] = {
            k: v for k, v in MaxURIerror.min_sizes.items()
        }
        content_identification: Callable = MaxURIerror.content_identification
        error_codes: Dict[int, Set[str]] = MaxURIerror.status
        status_responses: Set[int] = set()
        interval: int = self.interval
        response: HTTPResponse = None
        last_size: int = 0

        while len(maxsize_servers) > 1:
            if interval and response:
                sleep(interval)

            middle = round(median(maxsize_servers))

            if last_size == middle:
                logger_debug(
                    "Median is the same than the precedent request... "
                    f"Add 1 to the median ({middle})"
                )
                middle += 1

            response = self.request(*args, size=middle, **kwargs)

            status = response.status
            logger_debug(f"Request size: {middle}, response status: {status}.")

            if status in error_codes:
                if status not in status_responses:
                    servers = content_identification(response.read())

                    if servers is None:
                        pass
                    elif len(servers) == 1:
                        yield response, middle, servers
                        return None
                    else:
                        new_maxsize_servers = defaultdict(set)
                        for size, names in maxsize_servers.items():
                            for name in names:
                                if name in servers:
                                    new_maxsize_servers[size].add(name)

                        maxsize_servers = new_maxsize_servers

                    status_responses.add(status)

                condition = lt
            else:
                condition = ge

            maxsize_servers = {
                size: name
                for size, name in maxsize_servers.items()
                if condition(size, middle)
            }

            last_size = middle
            logger_debug(f"Servers size: {len(maxsize_servers)}.")
            yield response, middle, maxsize_servers.values()

        servers = self.compare_matching_servers(
            *maxsize_servers.popitem(), status_responses
        )

        yield response, middle, servers

    def compare_matching_servers(
        self, maxsize: int, server: Set[str], status_responses: Set[int]
    ) -> List[str]:

        """
        This function compares Web servers matching
        with the max URI size (using error codes).
        """

        logger_debug("Identifying the Web Server...")

        if not status_responses:
            return {"Busybox"}

        servers_: Set[str] = MaxURIerror.min_sizes[maxsize].copy()

        maxsize_servers_matching = len(servers_)

        if maxsize_servers_matching == 1:
            server = server.pop()
            logger_debug(
                f"Only one server ({server}) matching "
                f"with max URI size: {maxsize}"
            )
            servers = servers_
        else:
            logger_debug(
                f"There are {maxsize_servers_matching} servers matching with"
                f" max URI size: {maxsize}. Compare error codes..."
            )

            codes = MaxURIerror.status.copy()
            servers = {
                server_name
                for server_name in servers_
                for status in status_responses
                if server_name in codes[status]
            }

        return servers


def parse_args() -> Namespace:

    """
    This function parses command line arguments.
    """

    parser = ArgumentParser(
        description="This package identifies target's web server."
    )

    add_argument = parser.add_argument
    add_argument(
        "action",
        default="identify",
        choices={"identify", "getmaxuri"},
        help=(
            "Identify the target's web server or "
            "get the maximum size of the URI."
        ),
    )
    add_argument(
        "target",
        help="Host targeted (examples: 10.101.10.101:8000, example.com)",
    )
    add_argument(
        "--method",
        "-m",
        default="GET",
        help="HTTP method to request the Web Server",
    )
    add_argument(
        "--baseuri", "-b", default="/", help="Base URI to request the target."
    )
    add_argument("--interval", "-i", type=float, help="Requests interval.")
    add_argument(
        "--ssl", "-s", action="store_true", help="Use HTTPS (SSL, encryption)."
    )
    add_argument(
        "--timeout", "-t", type=int, help="Set timeout for HTTP requests."
    )
    add_argument(
        "--user-agent",
        "-u",
        default="WebServerIdentifier " + __version__,
        help="User-Agent header for the HTTP requests.",
    )

    parser.add_verbose(function=partial(printf, state="INFO"))
    parser.add_debug()

    return parser.parse_args()


def get_max_uri_size(
    identifier: WebServerIdentifier, method: str = "GET"
) -> int:

    """
    This function detects the maximum size of the target's URI.
    """

    for size, response in identifier.get_max_URI_size(method=method):
        verbose(
            f"Request size: {size}, response code: "
            f"{response.status!r} {response.reason!r}"
        )

        if isinstance(
            response, HTTPResponse
        ):  # CustomResponse raise exception
            last_response: HTTPResponse = response

    error_reason = identifier.error_reason
    printf(f"Server header: {last_response.getheader('Server', '')!r}")
    printf(
        f"Maximum URI length is: {size}, error code:"
        f" {identifier.error_status!r} {error_reason!r}"
    )

    return 0 if error_reason else 1


def identify_server(
    identifier: WebServerIdentifier, method: str = "GET"
) -> int:

    """
    This function prints the probable target's Web Server.
    """

    error_status: Dict[int, Set[str]] = MaxURIerror.status
    last_error: Union[HTTPResponse, CustomResponse] = CustomResponse(
        None, None
    )
    last_response = None

    for response, size, names in identifier.identify_server(method=method):
        status = response.status
        verbose(f"Response status: {status} for request size: {size}.")

        if status in error_status:
            last_error = response

        if isinstance(
            response, HTTPResponse
        ):  # CustomResponse raise exception
            last_response: HTTPResponse = response

    if last_response is None:
        last_response = identifier.request(method=method)

    printf(
        f"Server header: {last_response.getheader('Server', '')!r}, last"
        f" request size: {size!r}, last error code: {last_error.status!r},"
        f" server(s): {', '.join(names)!r}."
    )

    return 0


def main() -> int:

    """
    This function executes the module from the command line.
    """

    arguments: Namespace = parse_args()
    ssl = arguments.ssl
    action = arguments.action
    timeout = arguments.timeout

    logger_debug("Command line arguments parsed.")

    kwargs = {}
    if ssl:
        kwargs["context"] = _create_unverified_context()

    if timeout:
        kwargs["timeout"] = timeout

    identifier = WebServerIdentifier(
        arguments.target,
        arguments.baseuri,
        ssl,
        arguments.interval,
        arguments.user_agent,
        **kwargs,
    )
    logger_debug("Identifier built.")

    if action == "getmaxuri":
        return get_max_uri_size(identifier, method=arguments.method)
    elif action == "identify":
        return identify_server(identifier, method=arguments.method)

    return 0


logger: Logger = get_custom_logger(__name__)
logger_debug: Callable = logger.debug
logger_info: Callable = logger.info
logger_warning: Callable = logger.warning
logger_error: Callable = logger.error
logger_critical: Callable = logger.critical

print(copyright)

if __name__ == "__main__":
    exit(main())

# https://gist.github.com/willurd/5720255
