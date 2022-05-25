# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""Radial distribution function."""

import math
import logging

import numpy

from .helpers import linear_grid
from .correlation import Correlation
from .progress import progress

__all__ = ['RadialDistributionFunction',
           'RadialDistributionFunctionLegacy',
           'RadialDistributionFunctionFast']

_log = logging.getLogger(__name__)


def gr_kernel(x, y, L, *args):
    # Precalculating 1/L does not improve timings
    # r is an array of array distances
    r = x-y
    r = r - numpy.rint(r/L) * L
    return numpy.sqrt(numpy.sum(r**2, axis=1))


def gr_kernel_square(x, y, L, *args):
    """Return square distances."""
    # r is an array of array distances
    r = x-y
    r = r - numpy.rint(r/L) * L
    return numpy.sum(r**2, axis=1)

def pairs_newton_hist(f, x, y, L, bins):
    """
    Apply function f to all pairs in x[i] and y[j] and update the
    |hist| histogram using the |bins| bin edges.
    """
    hist, bins = numpy.histogram([], bins)
    # Do the calculation in batches to optimize
    bl = max(1, int(1e5 / len(y)))
    for ib in range(0, len(y)-1, bl):
        fxy = []
        # batch must never exceed len(y)-1
        for i in range(ib, min(ib+bl, len(y)-1)):
            for value in f(x[i+1:], y[i], L):
                fxy.append(value)
        hist_tmp, bins = numpy.histogram(fxy, bins)
        hist += hist_tmp
    return hist


def pairs_hist(f, x, y, L, bins):
    """
    Apply function f to all pairs in x[i] and y[j] and update the
    |hist| histogram using the |bins| bin edges.
    """
    hist, bins = numpy.histogram([], bins)
    for i in range(len(y)):
        fxy = f(x[:], y[i], L)
        hist_tmp, bins = numpy.histogram(fxy, bins)
        hist += hist_tmp
    return hist


class RadialDistributionFunctionLegacy(Correlation):
    """
    Radial distribution function.

    The correlation function g(r) is computed over a grid of distances
    `rgrid`. If the latter is `None`, the grid is linear from 0 to L/2
    with a spacing of `dr`. Here, L is the side of the simulation cell
    along the x axis at the first step.

    Additional parameters:
    ----------------------

    - norigins: controls the number of trajectory frames to compute
      the time average
    """

    nbodies = 2
    symbol = 'gr'
    short_name = 'g(r)'
    long_name = 'radial distribution function'
    phasespace = 'pos'

    def __init__(self, trajectory, rgrid=None, norigins=None, dr=0.04, ndim=-1, rmax=-1.0):
        Correlation.__init__(self, trajectory, rgrid, norigins=norigins)
        self.dr = dr
        self.rmax = rmax
        """
        Limit distance binning up to `rmax`. It may enable linked cells if
        this is advantageous.
        """

    def _setup_grid(self, system):
        """
        Deferred grid setup
        """
        if self.grid is None:
            # Get side of cell. If the system does not have a cell,
            # wrap it in an infinite cell and estimate a reasonable grid.
            ndims = system.number_of_dimensions
            if system.cell is not None:
                # Redefine grid to extend up to L
                # The grid will be cropped later to L/2
                # This retains the original dr
                self.grid = linear_grid(self.dr/2, min(system.cell.side), self.dr)
            else:
                # If there is no cell, then rmax must have been given
                # This retains the original dr
                if self.rmax > 0:
                    self.grid = linear_grid(self.dr/2, self.rmax, self.dr)
                else:
                    self.grid = linear_grid(self.dr/2, self.dr*1000, self.dr)

        # Internal max distance (/= user provided rmax)
        self._rmax = self.grid[-1]

    def _compute(self):
        ncfg = len(self.trajectory)
        system = self.trajectory.read(0)
        ndims = system.number_of_dimensions
        self._setup_grid(system)

        # Reconstruct bounds of grid for numpy histogram
        grid = []
        for i in range(len(self.grid)):
            grid.append(self.grid[i] - (self.grid[1] - self.grid[0]) / 2)
        grid.append(self.grid[-1] + (self.grid[1] - self.grid[0]) / 2)
        self.grid = grid
        gr, bins = numpy.histogram([], bins=self.grid)

        # Assume grandcanonical trajectory for generality.
        # Note that testing if the trajectory is grandcanonical or
        # semigrandcanonical is useless when applying filters.
        # N_0, N_1 = len(self._pos_0[0]), len(self._pos_1[0])
        N_0 = numpy.average([len(x) for x in self._pos_0])
        N_1 = numpy.average([len(x) for x in self._pos_1])

        gr_all = []
        _, r = numpy.histogram([], bins=self.grid)
        origins = range(0, ncfg, self.skip)
        for i in progress(origins):
            system = self.trajectory.read(i)
            side = system.cell.side
            if len(self._pos_0[i]) == 0 or len(self._pos_1[i]) == 0:
                continue
            if self._pos_0 is self._pos_1:
                gr = pairs_newton_hist(gr_kernel, self._pos_0[i], self._pos_1[i], side, r)
            else:
                gr = pairs_hist(gr_kernel, self._pos_0[i], self._pos_1[i], side, r)
            gr_all.append(gr)

        # Normalization
        volume = system.cell.volume
        if ndims == 2:
            vol = math.pi * (r[1:]**2 - r[:-1]**2)
        elif ndims == 3:
            vol = 4 * math.pi / 3.0 * (r[1:]**3 - r[:-1]**3)
        else:
            from math import gamma
            n2 = int(float(ndims) / 2)
            vol = math.pi**n2 * (r[1:]**ndims-r[:-1]**ndims) / gamma(n2+1)
        rho = N_1 / volume
        if self._pos_0 is self._pos_1:
            norm = rho * vol * N_0 * 0.5  # use Newton III
        else:
            norm = rho * vol * N_0
        gr = numpy.average(gr_all, axis=0)
        self.grid = (r[:-1] + r[1:]) / 2.0
        self.value = gr / norm
        # Restrict distances to L/2 (in last frame) or rmax
        if self.rmax > 0:
            where = self.grid <= self.rmax
        else:
            side = system.cell.side
            where = self.grid <= min(side) / 2
        self.grid = self.grid[where]
        self.value = self.value[where]


class RadialDistributionFunctionFast(RadialDistributionFunctionLegacy):
    """
    Radial distribution function using f90 kernel.

    The correlation function g(r) is computed over a grid of distances
    `rgrid`. If the latter is `None`, the grid is linear from 0 to L/2
    with a spacing of `dr`. Here, L is the side of the simulation cell
    along the x axis at the first step.

    Additional parameters:
    ----------------------

    - norigins: controls the number of trajectory frames to compute
      the time average
    """

    def _compute(self):
        from atooms.postprocessing.realspace_wrap import compute
        from atooms.postprocessing.linkedcells import LinkedCells

        # Assume grandcanonical trajectory for generality.
        # Note that testing if the trajectory is grandcanonical or
        # semigrandcanonical is useless when applying filters.
        N_0, N_1 = [], []
        gr_all = []

        # Grid setup.
        # Get side of cell. If the system does not have a cell,
        # wrap it in an infinite cell and estimate a reasonable grid.
        system = self.trajectory.read(0)
        ndims = system.number_of_dimensions
        self._setup_grid(system)
        dr = self.grid[1] - self.grid[0]
        gr = numpy.zeros(len(self.grid), dtype=int)
        bins = numpy.array(self.grid)

        # Use linked cells only if it is advantageous
        # - more than 3 cells along each side
        # - memory footprint is < ~1Gb
        # These tests are done of the first framce
        # TODO: if memory footprint is surpassed skip particles
        linkedcells = None
        if self.rmax > 0.0 and system.cell is not None:
            n_0 = len(self._pos_0[0])
            n_1 = len(self._pos_1[0])
            rho = n_1 / system.cell.volume
            nmax = self.rmax**ndims * rho
            if int(min(system.cell.side / self.rmax)) > 3 and nmax * n_0 < 1e6:
                _log.info('using linked cells')
                linkedcells = LinkedCells(rcut=self.rmax)
            else:
                _log.info('not using linked cells')
                linkedcells = None

        # Main loop for average
        origins = range(0, len(self.trajectory), self.skip)
        for i in progress(origins):
            # Skip if there are no particles
            if len(self._pos_0[i]) == 0 or len(self._pos_1[i]) == 0:
                continue

            # Switch between self and distinct calculation
            distinct = self._pos_0 is not self._pos_1

            # Store side
            system = self.trajectory.read(i)
            if system.cell is not None:
                side = system.cell.side
            else:
                import sys
                side = numpy.ndarray(ndims, dtype=float)
                side[:] = sys.float_info.max

            # When using linked cells, we precalculate the neighbors
            if linkedcells:
                if self._pos_0 is self._pos_1:
                    neighbors, number_of_neighbors = linkedcells.compute(side, self._pos_0[i], as_array=True)
                else:
                    neighbors, number_of_neighbors = linkedcells.compute(side, self._pos_0[i], self._pos_1[i], as_array=True)

            # Transpose the arrays for fortran
            # TODO: can we avoid this?
            if distinct:
                pos_0 = self._pos_0[i].transpose()
                pos_1 = self._pos_1[i].transpose()
            else:
                pos_0 = self._pos_0[i].transpose()
                pos_1 = pos_0

            # With a non-periodic cell, which just bounds the physical
            # domain, we must crop particles close to the surface
            # self_term = 0
            if hasattr(system.cell, 'periodic') and not numpy.any(system.cell.periodic):
                # mask = numpy.ndarray(pos_0.shape[1], dtype=numpy.bool)
                # TODO: bool does not work
                mask = compute.on_surface(pos_0, side, self.rmax)
                mask = mask == 1
                pos_0 = pos_0[:, mask]
                # Force distinct calculation
                distinct = True

            # Store number of particles for normalization
            N_0.append(pos_0.shape[1])
            N_1.append(pos_1.shape[1])

            # Compute g(r)
            if not distinct:
                if linkedcells is None:
                    compute.gr_self(pos_0, side, dr, gr, bins)
                else:
                    compute.gr_neighbors_self('C', pos_0, neighbors, number_of_neighbors, side, dr, gr, bins)
            else:
                if linkedcells is None:
                    compute.gr_distinct(pos_0, pos_1, side, dr, gr, bins)
                else:
                    compute.gr_neighbors_distinct('C', pos_0, pos_1, neighbors, number_of_neighbors, side, dr, gr, bins)

            # Damned copies in python
            gr_all.append(gr.copy())

        # Normalization
        # Array r is used to compute shells, we thus use the bin boundaries
        r = bins - (bins[1] - bins[0]) / 2
        N_0 = numpy.average(N_0)
        N_1 = numpy.average(N_1)
        if system.cell is not None:
            volume = system.cell.volume
        else:
            # TODO: this only works with recent atooms
            volume = len(system.particle) / system.density
        if ndims == 2:
            vol = math.pi * (r[1:]**2 - r[:-1]**2)
        elif ndims == 3:
            vol = 4 * math.pi / 3.0 * (r[1:]**3 - r[:-1]**3)
        else:
            from math import gamma
            n2 = int(float(ndims) / 2)
            vol = math.pi**n2 * (r[1:]**ndims-r[:-1]**ndims) / gamma(n2+1)

        rho = N_1 / volume
        norm = rho * vol * N_0
        if not distinct:
            # We used Newton III
            norm /= 2
        gr = numpy.average(gr_all, axis=0)

        # We crop the last entry
        self.grid = bins[:-1]
        self.value = gr[:-1] / norm

        # Restrict distances to L/2 (in last frame) or rmax
        if self.rmax > 0:
            where = self.grid <= self.rmax
        else:
            side = system.cell.side
            where = self.grid <= min(side) / 2
        self.grid = self.grid[where]
        self.value = self.value[where]


# Defaults to fast
try:
    import atooms.postprocessing.realspace_wrap
    RadialDistributionFunction = RadialDistributionFunctionFast
except ImportError:
    RadialDistributionFunction = RadialDistributionFunctionLegacy
