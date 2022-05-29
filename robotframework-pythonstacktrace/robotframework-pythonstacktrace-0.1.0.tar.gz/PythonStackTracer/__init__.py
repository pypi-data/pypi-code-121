# Copyright 2022- Piotr Chromiński
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

# pylint: disable=invalid-name, unused-argument
import sys
from dataclasses import dataclass, field
from typing import Any, List

from robot.utils import ErrorDetails


@dataclass
class PythonStackTracer:
    """Robot Framework listener which prints Python traceback for failing keywords."""

    ROBOT_LISTENER_API_VERSION = "2"
    _kwstack: List[Any] = field(default_factory=list)

    def start_test(self, name, attributes):
        self._kwstack = []

    def end_keyword(self, name, attributes):
        if attributes["status"] == "FAIL":
            self._kwstack.append((name, attributes, sys.exc_info()[1]))

    def end_test(self, data, result):
        if not self._kwstack:
            return

        for name, attributes, exc in reversed(self._kwstack):
            if name == "BuiltIn.Wait Until Keyword Succeeds":
                continue
            break
        else:
            return

        if attributes["libname"] == "BuiltIn":
            return

        error = ErrorDetails(exc)
        if error is None:
            return

        print("", end="\r")
        print(f"Python {error.traceback}")
        print("_" * 78)
