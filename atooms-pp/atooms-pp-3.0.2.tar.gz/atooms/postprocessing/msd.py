# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""Mean square displacement."""

import logging
import numpy

from .helpers import linear_grid
from .correlation import Correlation, gcf_offset
from .helpers import setup_t_grid

__all__ = ['MeanSquareDisplacement']

_log = logging.getLogger(__name__)


class MeanSquareDisplacement(Correlation):
    """
    Mean square displacement.

    If the time grid `tgrid` is None, the latter is redefined in a way
    controlled by the variable `rmax`. If `rmax` is negative
    (default), the time grid is linear between 0 and half of the
    largest time in the trajectory. If `rmax` is positive, the time
    grid comprises `tsamples` entries linearly spaced between 0 and
    the time at which the square root of the mean squared displacement
    reaches `rmax`.

    Additional parameters:
    ----------------------

    - sigma: value of the interparticle distance (usually 1.0). It is
    used to limit the fit range to extract the diffusion coefficient
    and to determine the diffusion time
    """

    symbol = 'msd'
    short_name = 'dr^2(t)'
    long_name = 'mean square displacement'
    phasespace = 'pos-unf'

    def __init__(self, trajectory, tgrid=None, rmax=-1.0, norigins=None,
                 tsamples=30, sigma=1.0, fix_cm=False, no_offset=False):
        self.rmax = rmax
        self.sigma = sigma
        self.tsamples = tsamples
        self._norigins = norigins
        # Offsets in time grid are only relevant with periodic blocks
        # Use the no_offset parameter to disable them
        self._no_offset = no_offset
        Correlation.__init__(self, trajectory, tgrid, norigins=norigins, fix_cm=fix_cm)

    def _compute(self):
        # We postpone time grid definition to compute to avoid
        # unfolding the trajectory twice when targeting the rmsd

        def msd(x, y):
            return numpy.sum((x-y)**2) / float(x.shape[0])

        if self.grid is None:
            t_max = self.trajectory.total_time
            if self.rmax > 0.0:
                msd_total = msd(self._pos_unf[-1], self._pos_unf[0])
                frac = self.rmax**2 / msd_total
                t_target = frac * t_max
                self.grid = linear_grid(0.0, min(t_max, t_target), self.tsamples)
            else:
                self.grid = linear_grid(0.0, t_max, self.tsamples)

        # Setup time grid
        # We disable offsets if only one time origin is requested or if no_offset is True
        self._discrete_tgrid = setup_t_grid(self.trajectory, self.grid,
                                            offset=self._norigins != '1' and not self._no_offset)
        # Note that the grid is redefined
        self.grid, self.value = gcf_offset(msd, self._discrete_tgrid, self.skip,
                                           self.trajectory.steps, self._pos_unf)
        # Update grid to real time
        self.grid = [ti * self.trajectory.timestep for ti in self.grid]

    def analyze(self):
        # Get the time when MSD equals sigma**2
        try:
            from .helpers import feqc
            self.analysis['diffusive time tau_D'] = feqc(self.grid, self.value, self.sigma**2)[0]
        except ValueError:
            self.analysis['diffusive time tau_D'] = None

        where = numpy.array(self.value) > self.sigma**2
        if sum(where) < 2:
            _log.warn('could not fit MSD: not enough data above sigma')
            return

        from .helpers import linear_fit
        diffusion = linear_fit(numpy.array(self.grid)[where],
                               numpy.array(self.value)[where])
        ndim = self.trajectory.read(0).number_of_dimensions
        self.analysis['diffusion coefficient D'] = diffusion[0] / (2*ndim)
