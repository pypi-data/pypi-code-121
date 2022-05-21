# Pure zero-dependency JSON-RPC 2.0 implementation.
# Copyright © 2022 Andrew Malchuk. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Final

from ._dispatcher import Dispatcher
from ._errors import Error, ErrorEnum
from ._request import BatchRequest, Request
from ._response import BatchResponse, Response
from ._serializer import JSONSerializer
from ._wsgi import WSGIHandler

__all__: Final[list[str]] = [
    "BatchRequest",
    "BatchResponse",
    "Dispatcher",
    "Error",
    "ErrorEnum",
    "JSONSerializer",
    "Request",
    "Response",
    "WSGIHandler"
]

__version__: Final[str] = "2.0.2"
