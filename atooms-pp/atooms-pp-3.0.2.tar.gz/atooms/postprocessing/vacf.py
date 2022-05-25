# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""Velocity autocorrelation function."""

import numpy

from .correlation import Correlation, gcf_offset
from .helpers import setup_t_grid, linear_grid

__all__ = ['VelocityAutocorrelation']


class VelocityAutocorrelation(Correlation):

    """Velocity autocorrelation function."""

    symbol = 'vacf'
    short_name = 'Z(t)'
    long_name = 'velocity autocorrelation'
    phasespace = ['vel']

    def __init__(self, trajectory, tgrid=None, tsamples=30, norigins=None):
        Correlation.__init__(self, trajectory, tgrid, norigins=norigins)
        if self.grid is None:
            self.grid = linear_grid(0.0, trajectory.total_time * 0.10, tsamples)
        self._discrete_tgrid = setup_t_grid(self.trajectory, tgrid, offset=norigins != '1')

    def _compute(self):
        def f(x, y):
            return numpy.sum(x * y) / float(x.shape[0])
        self.grid, self.value = gcf_offset(f, self._discrete_tgrid,
                                           self.trajectory.block_size,
                                           self.trajectory.steps,
                                           self._vel)
        self.grid = [ti * self.trajectory.timestep for ti in self.grid]
