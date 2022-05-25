# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""Four-point dynamic structure factor."""

import numpy

from .fourierspace import FourierSpaceCorrelation, expo_sphere
from .helpers import setup_t_grid
from .qt import self_overlap
from .progress import progress

__all__ = ['S4ktOverlap']


class S4ktOverlap(FourierSpaceCorrelation):
    """
    Four-point dynamic structure factor from time-dependent self overlap.

    See the documentation of the `FourierSpaceCorrelation` base class
    for information on the instance variables.
    """

    symbol = 's4kt'
    short_name = 'S_4(t,k)'
    long_name = '4-point dynamic structure factor from self overlap'
    phasespace = ['pos', 'pos-unf']

    # TODO: refactor a S4k base correlation that forces to implement tabulat method (e.g. overlap, Q_6, voronoi ...)
    # TODO: should we drop this instead and rely on F(k,t) with grandcanonical

    def __init__(self, trajectory, tgrid, kgrid=None, norigins=-1,
                 nk=20, dk=0.1, a=0.3, kmin=1.0, kmax=10.0, ksamples=10):
        FourierSpaceCorrelation.__init__(self, trajectory, [tgrid, kgrid], norigins,
                                         nk, dk, kmin, kmax, ksamples)
        # Setup time grid
        self._discrete_tgrid = setup_t_grid(self.trajectory, tgrid, offset=norigins != '1')
        self.a_square = a**2

    def _tabulate_W(self, kgrid, selection, t_off, t, skip):
        """
        Tabulate W
        """
        side = self.trajectory[0].cell.side
        nt = range(t_off, len(self._pos)-t, skip)
        W = {}
        for i_0, t_0 in enumerate(nt):
            expo = expo_sphere(self.k0, self._koffset, self._pos[t_0])
            for k, klist in self._kvectors:
                for kvec in klist:
                    if kvec not in W:
                        W[kvec] = numpy.ndarray(len(nt), dtype=complex)
                    W[kvec][i_0] = numpy.sum(self_overlap(self._pos_unf[t_0], self._pos_unf[t_0+t], side, self.a_square) *
                                             expo[..., 0, kvec[0]] * expo[..., 1, kvec[1]] * expo[..., 2, kvec[2]])
        return W

    def _compute(self):
        # We expect there is only one time in tgrid.
        # We could easily workaround it by outer looping over i
        # We do not expect to do it for many times (typically we show S_4(k,tau_alpha) vs k)
        dt = []
        self.value = []
        for off, i in progress(self._discrete_tgrid):
            # As for fkt
            W = self._tabulate_W(self.kgrid, self.selection, off, i, self.skip)

            # Compute variance of W
            w_av = [complex(0., 0.) for _ in self.kgrid]
            w2_av = [complex(0., 0.) for _ in self.kgrid]
            for k, klist in self._kvectors:
                for kvec in klist:
                    # Comupte |<W>|^2  and <W W^*>
                    w_av[kk] = numpy.average(W[kvec])
                    w2_av[kk] = numpy.average(W[kvec] * W[kvec].conjugate())

            # Normalization
            npart = self._pos[0].shape[0]
            dt.append(self.trajectory.timestep * (self.trajectory.steps[off+i] - self.trajectory.steps[off]))
            self.value.append([float(w2_av[k] - (w_av[k]*w_av[k].conjugate())) / npart for k in range(len(self.grid[1]))])
        self.grid[1] = self.kgrid
        self.grid[0] = dt
