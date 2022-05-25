# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""Four-point dynamic susceptibility."""

import logging
import numpy

from .helpers import logx_grid
from .correlation import Correlation
from .helpers import setup_t_grid, ifabsmm
from .qt import self_overlap
from .progress import progress

__all__ = ['Chi4SelfOverlap', 'Chi4SelfOverlapOptimized']

_log = logging.getLogger(__name__)


class Chi4SelfOverlap(Correlation):
    """
    Four-point dynamic susceptibility from the time-dependent self
    overlap function.

    Parameters:
    -----------

    - a: distance parameter entering the Heaviside function in the
    overlap calculation
    """

    symbol = 'chi4qs'
    short_name = 'chi_4(t)'
    long_name = 'dynamic susceptibility of self overlap'
    phasespace = 'pos-unf'

    def __init__(self, trajectory, tgrid=None, norigins=-1, a=0.3,
                 tsamples=60):
        Correlation.__init__(self, trajectory, tgrid, norigins=norigins)
        if tgrid is None:
            self.grid = logx_grid(0.0, self.trajectory.total_time * 0.75, tsamples)
        self._discrete_tgrid = setup_t_grid(self.trajectory, self.grid, offset=norigins != '1')
        self.a_square = a**2
        self.average = Correlation(self.trajectory, self.grid)
        self.average.short_name = 'Q^u(t)'
        self.average.symbol = 'qsu'
        self.average.long_name = 'Average of self overlap, not normalized'
        self.variance = Correlation(self.trajectory, self.grid)
        self.variance.short_name = 'Q_2^u(t)'
        self.variance.symbol = 'q2su'
        self.variance.long_name = 'Variance of self overlap, not normalized'

    def _compute(self):
        def f(x, y):
            return self_overlap(x, y, self.a_square).sum()

        side = self.trajectory.read(0).cell.side
        self.grid = []
        # At this stage, we can copy the tags
        self.average.tag, self.variance.tag = self.tag, self.tag
        for off, i in progress(self._discrete_tgrid):
            A, A2, cnt = 0.0, 0.0, 0
            for i0 in range(off, len(self._pos_unf)-i-self.skip, self.skip):
                w = f(self._pos_unf[i0], self._pos_unf[i0 + i])
                A2 += w**2
                A += w
                cnt += 1
            dt = self.trajectory.steps[off+i] - self.trajectory.steps[off]
            if cnt > 0:
                A_av, A2_av = A / cnt, A2 / cnt
            else:
                A_av, A2_av = 0, 0
            self.grid.append(dt * self.trajectory.timestep)
            self.value.append((A2_av - A_av**2) / self._pos_unf[0].shape[0])
            self.average.value.append(A_av)
            self.variance.value.append(A2_av)
        self.average.grid, self.variance.grid = self.grid, self.grid

    def write(self):
        # We subclass this to also write down qsu and qsu2
        super(Chi4SelfOverlap, self).write()
        self.average.write()
        self.variance.write()

    def analyze(self):
        try:
            self.analysis['peak time tau_star'], self.analysis['peak height chi4_star'] = ifabsmm(self.grid, self.value)[1]
        except ZeroDivisionError:
            _log.warning('could not find maximum')


class Chi4SelfOverlapOptimized(Chi4SelfOverlap):
    """
    Four-point dynamic susceptibility from the time-dependent self
    overlap function.

    Optimized version using fortran 90 extension.
    """

    def _compute(self):
        try:
            from atooms.postprocessing.realspace_wrap import realspace_module
        except ImportError:
            _log.error('f90 wrapper missing or not functioning')
            raise

        def f(x, y):
            return realspace_module.self_overlap(x, y, numpy.array(self.a_square))

        self.grid = []
        self.average.tag, self.variance.tag = self.tag, self.tag
        for off, i in progress(self._discrete_tgrid):
            A, A2, cnt = 0.0, 0.0, 0
            for i0 in range(off, len(self._pos_unf)-i-self.skip, self.skip):
                w = f(self._pos_unf[i0], self._pos_unf[i0+i])
                A2 += w**2
                A += w
                cnt += 1
            dt = self.trajectory.steps[off+i] - self.trajectory.steps[off]
            A_av, A2_av = A/cnt, A2/cnt
            self.grid.append(dt * self.trajectory.timestep)
            self.value.append((A2_av - A_av**2) / self._pos_unf[0].shape[0])
            self.average.value.append(A_av)
            self.variance.value.append(A2_av)
        self.average.grid, self.variance.grid = self.grid, self.grid
