#
#
# voice-skill-sdk
#
# (C) 2021, Deutsche Telekom AG
#
# This file is distributed under the terms of the MIT license.
# For details see the file LICENSE in the top directory.
#

"""Error responses"""

from enum import IntEnum
from typing import Any, Optional, Text
from pydantic import BaseModel


class ErrorCode(IntEnum):
    """Skill SPI error response codes"""

    # skill invoke with a wrong intent
    NOT_FOUND = 1

    # given third party token is invalid
    INVALID_TOKEN = 2

    # expected arguments like locale are missing
    BAD_REQUEST = 3

    # timeout
    TIMEOUT = 4

    # not considered situation, unhandled exception
    INTERNAL_ERROR = 999


class ErrorResponse(BaseModel):
    """
    An error response

    It can be returned explicitly from the intent handler or will be returned if calling the intent handler fails.

    The following combinations are defined:

    **wrong intent**
      ``{"code": 1, "text": "intent not found"}`` HTTP code: *404*

    **invalid token**
      ``{"code": 2, "text": "invalid token"}`` HTTP code: *400*

    **version, locale,… missing**
      ``{"code": 3, "text": "Bad request"}`` HTTP code: *400*

    **time out**
      ``{"code": 4, "text": "Time out"}`` HTTP code: *504*

    **unhandled exception**
      ``{"code": 999, "text": "internal error"}`` HTTP code: *500*

    """

    code_map = {1: (404,), 2: (400,), 3: (400,), 4: (504,), 999: (500,)}

    # Error code
    code: ErrorCode

    # Error message
    text: Text

    # Details (if in debug mode)
    detail: Optional[Any]
