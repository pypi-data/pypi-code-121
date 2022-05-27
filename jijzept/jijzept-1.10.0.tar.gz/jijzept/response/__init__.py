from pkgutil import extend_path

__path__ = extend_path(__path__, __name__)

import jijzept.response.base
import jijzept.response.base as base
import jijzept.response.dimodresopnse
import jijzept.response.dimodresopnse as dimodresopnse

from jijzept.response.base import APIStatus, BaseResponse
from jijzept.response.dimodresopnse import DimodResponse

__all__ = [
    "APIStatus",
    "BaseResponse",
    "DimodResponse",
]
