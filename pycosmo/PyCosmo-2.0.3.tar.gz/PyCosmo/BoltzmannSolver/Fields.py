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

from collections import defaultdict

import numpy as np


class Fields(object):
    """
    Class for linear perturbations field objects.
    Usage example: fields.delta(5) returns the dark matter density perturbation at the
    5th time step
    """

    def __init__(
        self,
        cosmology,
    ):
        self._cosmology = cosmology
        self._wrapper = cosmology._wrapper

        self._y = None
        self.lna = None
        self._offsets = defaultdict(list)

    def set_results(self, lna, solver_result, keep_lna0):
        self.lna = lna

        fields_map = self._wrapper.fields(lna, solver_result, self._cosmology)

        offsets = defaultdict(list)
        self._symbols = []
        _y = []
        for i, (symbol, yvec) in enumerate(fields_map.items()):
            self._symbols.append(symbol)
            _y.append(yvec)

            if "[" not in symbol:
                offsets[symbol] = i
                continue

            index = int(symbol.split("[")[1].split("]")[0])
            stem = symbol.split("[")[0]
            offsets[stem].append((index, i))

        self._y = np.array(_y)
        assert self._y.shape[1] == len(lna), "fields and lna vector mismatch"
        self._offsets = offsets

        if not keep_lna0:
            self._y = self._y[:, 1:]
            self.lna = self.lna[1:]

    def __dir__(self):
        return super().__dir__() + list(map(str, self._symbols))

    def __getattr__(self, symbol):

        # needed to support pickling:
        if "_offsets" not in vars(self):
            raise AttributeError()

        if symbol not in self._offsets:
            return self.__getattribute__(symbol)

        index = self._offsets[symbol]
        if isinstance(index, int):
            return self._y[index, :]

        assert isinstance(index, list)
        index = [j for (i, j) in sorted(index)]
        return VectorWrapper(self._y, index)

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, dd):
        self.__dict__.update(dd)

    @property
    def a(self):
        """
        a(a_index): scale factor [1]
        """
        return np.exp(self.lna)

    @property
    def d_t(self):
        """
        d_t: time step in ln(a) units (one fewer value than ln(a) [1]
        """
        a = self.a
        return a[1:] - a[:-1]


class VectorWrapper:
    def __init__(self, y, indices):
        self.y = y
        self.indices = indices

        # supports conversion to np.ndarray using np.array(...):
        # (inspired from https://stackoverflow.com/questions/39376892/)
        data = y[indices, :]
        self.__array_interface__ = dict(
            shape=data.shape,
            typestr=data.dtype.kind,
            data=data.__array_interface__["data"],
        )

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):
        return self.y[self.indices[index], :]
