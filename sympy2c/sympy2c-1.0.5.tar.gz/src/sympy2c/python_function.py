# This file is part of sympy2c.
#
# Copyright (C) 2013-2022 ETH Zurich, Institute for Particle and Astrophysics and SIS
# ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

import hashlib
import inspect
from textwrap import dedent
from types import FunctionType

from .wrapper import WrapperBase


class PythonFunction:
    def __init__(self, function):
        assert isinstance(function, FunctionType)
        self.function_src = inspect.getsource(function)
        self.name = function.__name__
        self._unique_id = None

    def get_unique_id(self):
        if self._unique_id is None:
            md5 = hashlib.md5()
            md5.update(self.function_src.encode("utf-8"))
            self._unique_id = md5.hexdigest()
        return self._unique_id

    def wrapper(self):
        return PythonFunctionWrapper(self.name, self.function_src)


class PythonFunctionWrapper(WrapperBase):
    def __init__(self, name, function_src):
        self.name = name
        self.function_src = function_src
        self._unique_id = None

    def c_header(self):
        return ""

    def c_code(self, header_file_path):
        return ""

    def cython_code(self, header_file_path):
        return dedent(self.function_src)

    def determine_required_extra_wrappers(self):
        pass

    def setup_code_generation(self):
        pass

    def get_unique_id(self):
        if self._unique_id is None:
            md5 = hashlib.md5()
            md5.update(self.function_src.encode("utf-8"))
            self._unique_id = md5.hexdigest()
        return self._unique_id
