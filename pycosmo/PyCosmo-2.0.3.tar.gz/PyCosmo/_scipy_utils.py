# This file is part of PyCosmo, a multipurpose cosmology calculation tool in Python.
#
# Copyright (C) 2013-2021 ETH Zurich, Institute for Particle and Astrophysics and SIS
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


from scipy.interpolate import interp1d as _interp1d


class interp1d(object):

    """original interp1d can not be pickled. This class solves this"""

    def __init__(self, x, y, *args, **kws):
        self.x = x
        self.y = y
        self.args = args
        self.kws = kws
        self._setup()

    def _setup(self):
        self.function = _interp1d(self.x, self.y, *self.args, **self.kws)

    def __call__(self, *args, **kws):
        return self.function(*args, **kws)

    def __getstate__(self):
        return self.x, self.y, self.args, self.kws

    def __setstate__(self, data):
        self.x, self.y, self.args, self.kws = data
        self._setup()
