"""This module defines parsers and validators for JSON data.

SPDX-License-Identifier: AGPL-3.0-only OR BSD-3-Clause-Clear
"""

from ._base import Union, Parser, SimpleValue
from ._enum import EnumValue, StringEnum
from ._lazy import Lazy
from ._list import List, TwoTuple
from ._query import QueryParam
from ._convert import ConvertCtx, ConvertPriority, as_converter
from ._literal import LiteralBoolean
from ._mapping import (
    FixedMapping, LookupMapping, OnExtraAction, DefaultArgument,
    BaseFixedMapping, OptionalArgument, RequiredArgument, _DictGetter
)
from ._nullable import Nullable
from ._any_value import AnyValue
from ._multipart import (
    MultipartUploadWithData, MultipartUploadWithoutData,
    ExactMultipartUploadWithData
)
from .exceptions import ParseError, SimpleParseError, MultipleParseErrors
from ._rich_value import RichValue
from ._swaggerize import swaggerize, process_query_params
from ._parse_utils import Transform
from ._swagger_utils import OpenAPISchema
