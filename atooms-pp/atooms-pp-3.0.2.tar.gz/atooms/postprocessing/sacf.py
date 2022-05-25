#!/usr/bin/env python
# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""Stress autocorrelation function."""

import numpy

from .correlation import Correlation, gcf_offset
from .helpers import setup_t_grid

__all__ = ['StressAutocorrelation']


class StressAutocorrelation(Correlation):

    """Stress autocorrelation function."""

    symbol = 'sacf'
    short_name = 'S(t)'
    long_name = 'stress autocorrelation'
    phasespace = ['vel']

    def __init__(self, trajectory, tgrid, norigins=None):
        Correlation.__init__(self, trajectory, tgrid, norigins=norigins)
        self._discrete_tgrid = setup_t_grid(self.trajectory, tgrid, offset=norigins != '1')

    def _get_stress(self):
        ndims = 3
        p = self.trajectory.read(0).particle
        mass = numpy.array([pi.mass for pi in p])
        self._stress = []
        for i in self.trajectory.samples:
            s = self.trajectory.read(i).interaction.stress
            smk = numpy.zeros(ndims)
            m = 0
            for j in range(ndims):
                for k in range(j+1, ndims):
                    smk[m] = s[j, k] + numpy.sum(mass[:] * self._vel[i][:, j] * self._vel[i][:, k])
                    m += 1
            self._stress.append(smk)

    def _compute(self):
        def f(x, y):
            return numpy.sum(x*y) / float(x.shape[0])

        self._get_stress()
        V = self.trajectory.read(0).cell.volume
        self.grid, self.value = gcf_offset(f, self._discrete_tgrid, self.trajectory.block_size,
                                           self.trajectory.steps, self._stress)
        self.value = [x / V for x in self.value]
        self.grid = [ti * self.trajectory.timestep for ti in self.grid]

    def analyze(self):
        pass
