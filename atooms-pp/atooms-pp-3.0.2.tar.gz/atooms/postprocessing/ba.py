# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""Bond angle distribution."""

import math
import logging

import numpy

from .helpers import linear_grid
from .correlation import Correlation
from .progress import progress

__all__ = ['BondAngleDistribution']

_log = logging.getLogger(__name__)


def _default_rcut(th):
    """
    Look for the first minimum in the partial g(r)
    """
    from atooms.system.particle import distinct_species
    from atooms.postprocessing.partial import Partial
    from atooms.postprocessing import RadialDistributionFunction
    from .helpers import ifabsmm

    ids = distinct_species(th[0].particle)
    gr = Partial(RadialDistributionFunction, ids, th, dr=0.1)
    gr.do(update=False)
    rcut = {}
    for isp in ids:
        for jsp in ids:
            # First find absolute maximum
            _, m = ifabsmm(list(gr.partial[(isp, jsp)].grid),
                           list(gr.partial[(isp, jsp)].value))
            # Then look for first minimum after the maximum
            for i in range(len(gr.partial[(isp, jsp)].grid)):
                if gr.partial[(isp, jsp)].grid[i] >= m[0]:
                    delta = gr.partial[(isp, jsp)].value[i+1] - gr.partial[(isp, jsp)].value[i]
                    if delta >= 0:
                        rcut[(isp, jsp)] = gr.partial[(isp, jsp)].grid[i]
                        break

    return rcut

class BondAngleDistribution(Correlation):
    """
    Bond angle distribution function.
    """

    nbodies = 2
    symbol = 'ba'
    short_name = 'D(theta)'
    long_name = 'bond angle distribution'
    phasespace = ['pos', 'ids']

    def __init__(self, trajectory, norigins=None, dtheta=4.0, rcut=None):
        Correlation.__init__(self, trajectory, None, norigins=norigins)
        self.grid = linear_grid(0.0, 180.0, dtheta)  # reassign grid anyway
        self.rcut = rcut

    def _compute(self):
        from atooms.trajectory.decorators import change_species
        from atooms.postprocessing.realspace_wrap import compute
        from atooms.system.particle import distinct_species

        hist_all = []
        hist_one = numpy.ndarray(len(self.grid), dtype=numpy.int32)
        origins = range(0, len(self.trajectory), self.skip)
        dtheta = self.grid[1] - self.grid[0]

        # Setup array of cutoff distances based on g(r) calculated for
        # the whole trajectory.
        # We store the cutoffs into a (nsp, nsp) array
        # where the index follows the alphabetic order of species names
        ids = distinct_species(self.trajectory[0].particle)
        if self.rcut is None:
            rcut = _default_rcut(self.trajectory)
            self.rcut = numpy.ndarray((len(ids), len(ids)))
            for species_pair in rcut:
                self.rcut[ids.index(species_pair[0]), ids.index(species_pair[1])] = rcut[species_pair]
        else:
            self.rcut = numpy.array(self.rcut)

        for isp in range(len(ids)):
            for jsp in range(len(ids)):
                self.analysis['cutoff distance {}-{}'.format(isp, jsp)] = self.rcut[isp, jsp]

        for i in progress(origins):
            system = self.trajectory[i]
            side = system.cell.side  # this should not be affected by filters
            # system = change_species(system, 'F')  # species are in fortran style
            # ids = numpy.array(system.dump('spe'), dtype=numpy.int32)
            nn = numpy.array(0, dtype=numpy.int32)
            neighbors = numpy.ndarray(50, dtype=numpy.int32)
            for idx in range(len(self._pos_0[i])):
                isp = self._ids_0[i][idx]
                compute.neighbors('C', side, self._pos_0[i][idx],
                                  self._pos_1[i].transpose(),
                                  self._ids_1[i],
                                  self.rcut[isp, :],
                                  nn, neighbors)
                # print idx, self._pos_1[i].shape, neighbors[0: nn], set(self._ids_1[i])
                compute.bond_angle(self._pos_0[i][idx, :],
                                   self._pos_1[i].transpose(),
                                   neighbors[0: nn], side, dtheta,
                                   hist_one)
                hist_all.append(hist_one.copy())

        # Normalization
        hist = numpy.sum(hist_all, axis=0)
        norm = float(numpy.sum(hist[:-1]))
        self.grid = (numpy.array(self.grid[:-1]) + numpy.array(self.grid[1:])) / 2.0
        self.value = hist[:-1] / (norm * dtheta)
