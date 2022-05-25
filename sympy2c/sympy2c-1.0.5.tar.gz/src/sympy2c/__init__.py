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

# flake8: noqa F401

from .compiler import compile_if_needed_and_load
from .expressions import Max, Min, isnan
from .function import Alias, Function
from .globals import Globals
from .integral import ERROR, Checked, IfThenElse, Integral
from .interpolation import InterpolationFunction1D, InterpolationFunction1DInstance
from .module import Module
from .ode import Ode
from .ode_combined import OdeCombined
from .ode_fast import OdeFast
from .python_function import PythonFunction
from .symbol import Symbol, symbols
from .vector import Vector, VectorElement
from .version import __version__

__author__ = "Uwe Schmitt"
__email__ = "uwe.schmitt@id.ethz.ch"
