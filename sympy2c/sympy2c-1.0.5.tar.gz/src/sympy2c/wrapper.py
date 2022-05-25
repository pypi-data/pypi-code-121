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

import abc


class WrapperBase(abc.ABC):
    @abc.abstractmethod
    def c_header(self):
        ...

    @abc.abstractmethod
    def c_code(self, header_file_path):
        ...

    @abc.abstractmethod
    def cython_code(self, header_file_path):
        ...

    @abc.abstractmethod
    def determine_required_extra_wrappers(self):
        ...

    @abc.abstractmethod
    def setup_code_generation(self):
        ...
