# This file is part of atooms
# Copyright 2010-2018, Daniele Coslovich

"""Fourier-space post processing code."""

import math
import logging
import random
from collections import defaultdict

import numpy

from .helpers import linear_grid
from .correlation import Correlation

__all__ = ['expo_sphere', 'expo_sphere_safe', 'FourierSpaceCorrelation']

_log = logging.getLogger(__name__)


def expo_sphere(k0, nk_max, pos):
    """Returns the exponentials of the input positions for each k."""

    # Technical note: we use ellipsis, so that we can pass either a
    # single sample or multiple samples without having to add a
    # trivial extra dimension to input array
    im = numpy.complex(0.0, 1.0)
    # The integer grid must be the same as the one set in kgrid,
    # otherwise there is an offset the problem is that integer
    # negative indexing is impossible in python and rounding or
    # truncating kmax can slightly offset the grid

    # We pick up the smallest k0 to compute the integer grid
    # This leaves many unused vectors in the other directions, which
    # could be dropped using different nkmax for x, y, z
    # The shape of expo is nframes, N, ndim, 2*nk+1
    expo = numpy.ndarray((len(pos), ) + pos[0].shape + (2*nk_max+1, ), numpy.complex128)
    expo[..., nk_max] = numpy.complex(1.0, 0.0)
    # First fill positive k
    for j in range(pos[0].shape[-1]):
        expo[..., j, nk_max+1] = numpy.exp(im * k0[j] * pos[..., j])
        expo[..., j, nk_max-1] = expo[..., j, nk_max+1].conjugate()
        for i in range(2, nk_max):
            expo[..., j, nk_max+i] = expo[..., j, nk_max+i-1] * expo[..., j, nk_max+1]
    # Then take complex conj for negative ones
    for i in range(2, nk_max+1):
        # TODO: why is this line necessary?
        expo[..., nk_max+i] = expo[..., nk_max+i-1] * expo[..., nk_max+1]
        expo[..., nk_max-i] = expo[..., nk_max+i].conjugate()

    return expo


def expo_sphere_safe(k0, kmax, pos):
    """
    Returns the exponentials of the input positions for each k.
    It does not use ellipsis.
    """
    im = numpy.complex(0.0, 1.0)
    ndims = pos.shape[-1]
    nk_max = 1 + int(kmax / min(k0))
    expo = numpy.ndarray(pos.shape + (2*nk_max+1, ), numpy.complex128)
    expo[:, :, :, nk_max] = numpy.complex(1.0, 0.0)

    for j in range(ndims):
        expo[:, :, j, nk_max+1] = numpy.exp(im*k0[j]*pos[:, :, j])
        expo[:, :, j, nk_max-1] = expo[:, :, j, nk_max+1].conjugate()
        for i in range(2, nk_max):
            expo[:, :, j, nk_max+i] = expo[:, :, j, nk_max+i-1] * expo[:, :, j, nk_max+1]

    for i in range(2, nk_max+1):
        expo[:, :, :, nk_max+i] = expo[:, :, :, nk_max+i-1] * expo[:, :, :, nk_max+1]
        expo[:, :, :, nk_max-i] = expo[:, :, :, nk_max+i].conjugate()

    return expo


def _k_norm(ik, k0, offset):
    k_shift = k0 * (numpy.array(ik) - offset)
    k_sq = numpy.dot(k_shift, k_shift)
    return math.sqrt(k_sq)

def _sphere(kmax):
    ikvec = numpy.ndarray(3, dtype=int)
    for ix in range(-kmax, kmax+1):
        for iy in range(-kmax, kmax+1):
            for iz in range(-kmax, kmax+1):
                ikvec[0] = ix
                ikvec[1] = iy
                ikvec[2] = iz
                yield ikvec

def _disk(kmax):
    ikvec = numpy.ndarray(2, dtype=int)
    for ix in range(-kmax, kmax+1):
        for iy in range(-kmax, kmax+1):
            ikvec[0] = ix
            ikvec[1] = iy
            yield ikvec


class FourierSpaceCorrelation(Correlation):

    """
    Base class for Fourier space correlation functions.

    The correlation function is computed for each of the scalar values
    k_i of the provided `kgrid`. If the latter is `None`, the grid is
    built using `ksamples` entries linearly spaced between `kmin` and
    `kmax`.

    For each sample k_i in `kgrid`, the correlation function is
    computed over at most `nk` wave-vectors (k_x, k_y, k_z) such that
    their norm (k_x^2+k_y^2+k_z^2)^{1/2} lies within `dk` of the
    prescribed value k_i.

    See the doc of `Correlation` for information about the rest of the
    instance variables.
    """

    def __init__(self, trajectory, grid, norigins=None, nk=8, dk=0.1,
                 kmin=-1, kmax=10, ksamples=20, fix_cm=False, normalize=True):
        """
        Possible inputs:

        1. kgrid is None:

        the k grid is determined internally from kmin, kmax, ksamples
        and the kvectors are sampled using nk and dk parameters

        2. kgrid is not None, via grid or setting the variable after
        construction:

        kvectors are sampled using nk and dk and the kgrid is
        eventually redefined so that its values correspond exactly to
        the norms of the kvectors in each group

        3. kvectors is not None or set after construction: 

        kvectors must be a list of lists of kvectors in natural units

        Internal variables:

        - k0 : norm of the smallest kvector allowed by cell,
          determined internally at compute time.

        - _kvectors: list of lists of ndim arrays, grouped by
          the averaged norm, whose indices are (ix, iy, iz), which
          identify the kvectors according to the following
          formulas. We write kvectors as

          k = k0 * (jx, jy, jz)

          where jx, jy, jz are relative numbers. We tabulate
          exponentials over a grid and the indices (ix, iy, iz) of the
          tabulated array obey Fortran indexing. We symmetrize the j
          indices like this
          
          ix = jx + offset_j + 1, iy = jy + offset_j + 1, iz = jz + offset_j + 1
        
          where offset_j is the absolute value of the minimum of the
          whole set of (jx, jy, jz). This way we are sure that indices
          start from 1. This is necessary with numpy arrays, for which
          negative indices have a different meaning.

        - _koffset: value of offset_j defined above
        """
        super(FourierSpaceCorrelation, self).__init__(trajectory,
                                                      grid, norigins=norigins, fix_cm=fix_cm)
        # Some additional variables. k0 = smallest wave vectors
        # compatible with the boundary conditions
        self.normalize = normalize
        self.nk = nk
        self.dk = dk
        self.kmin = kmin
        self.kmax = kmax
        self.ksamples = ksamples
        self.kgrid = None
        self.k0 = []
        self._kvectors = []
        self._koffset = 0

    def compute(self):
        # Setup grid once. If cell changes we'll call it again
        self._setup()
        # Now compute
        super(FourierSpaceCorrelation, self).compute()

    def _setup(self, sample=0):
        # We skip setup if the kgrid is already set up and we are not
        # asking to rebuild it (for a sample != 0).
        # This allows to copy over the kvectors and kgrid
        if sample == 0 and self.kgrid is not None:
            return
        
        # We subclass compute to define k grid at compute time
        # Find k-norms grid and store it a self.kgrid (the norms are sorted)
        variables = self.short_name.split('(')[1][:-1]
        variables = variables.split(',')
        if len(variables) > 1:
            self.kgrid = self.grid[variables.index('k')]
        else:
            self.kgrid = self.grid

        # Smallest kvector
        self.k0 = 2*math.pi/self.trajectory[sample].cell.side
        # If grid is not provided, setup a linear grid from kmin,kmax,ksamples data
        # TODO: This shouldnt be allowed with fluctuating cells
        # Or we should fix the smallest k to some average of smallest k per sample
        if self.kgrid is None:
            if self.kmin > 0:
                self.kgrid = linear_grid(self.kmin, self.kmax, self.ksamples)
            else:
                self.kgrid = linear_grid(min(self.k0), self.kmax, self.ksamples)
        else:
            # Sort, since code below depends on kgrid[0] being the smallest k-value.
            self.kgrid.sort()
            # If the first wave-vector is negative we replace it by k0
            if self.kgrid[0] < 0.0:
                self.kgrid[0] = min(self.k0)

        # Setup the grid of wave-vectors
        self._kvectors, self._koffset = self._setup_grid_sphere(len(self.kgrid) * [self.dk],
                                                               self.kgrid, self.k0)

        # Decimate
        # Setting the seed here once so as to get the same set
        # independent of filters.
        random.seed(1)
        # Pick up a random, unique set of nk vectors out ot the avilable ones
        # without exceeding maximum number of vectors in shell nkmax
        # self.kgrid, self.selection = self._decimate_k()
        for i, klist in enumerate(self._kvectors):
            nk = min(self.nk, len(klist))
            self._kvectors[i] = random.sample(klist, nk)
        
        # Define the grid using the actual kvectors
        # average k norms appear after decimation.
        for i, klist in enumerate(self._kvectors):
            self.kgrid[i] = numpy.mean([_k_norm(kvec, self.k0, self._koffset) for kvec in klist])
        
    @staticmethod
    def _setup_grid_sphere(dk, kgrid, k0):
        """
        Setup wave vector grid with spherical average (no symmetry),
        picking up vectors that fit into shells of width `dk` centered around
        the values specified in the input list `kgrid`.

        Returns a list of lists of kvectors, one entry for each element in the grid.
        """
        _log.info('setting up the wave-vector grid')
        kvec = [[] for _ in range(len(kgrid))] #defaultdict(list)
        
        # With elongated box, we choose the smallest k0 component to
        # setup the integer grid. This must be consistent with
        # expo_grid() otherwise it wont find the vectors
        kmax = kgrid[-1] + dk[-1]
        kbin_max = 1 + int(kmax / min(k0))
        kmax_sq = kmax**2

        # Choose iterator of spatial grid
        ndims = len(k0)
        if ndims == 3:
            _iterator = _sphere
        elif ndims == 2:
            _iterator = _disk
        else:
            raise ValueError('unsupported dimension {}'.format(ndims))

        # Fill kvec array with kvectors matching the input kgrid within dk
        for ik in _iterator(kbin_max):
            ksq = numpy.dot(k0*ik, k0*ik)
            if ksq > kmax_sq:
                continue
            # beware: numpy.sqrt is x5 slower than math one!
            knorm = math.sqrt(ksq)
            # Look for a shell of vectors in which the vector could fit.
            # This expression is general and allows arbitrary k grids
            # However, searching for the shell like this is not fast
            # (it costs about as much as the above)
            for i in range(len((kgrid))):
                if abs(knorm - kgrid[i]) < dk[i]:
                    kvec[i].append(tuple(ik + kbin_max))
                    break

        # Check
        all_good = True
        for i in range(len(kvec)):
            if len(kvec[i]) == 0:
                dk[i] *= 1.2
                _log.info('increasing kbin {} to {}'.format(i, dk[i]))
                all_good = False
        if not all_good:
            return FourierSpaceCorrelation._setup_grid_sphere(dk, kgrid, k0)
        else:
            return kvec, kbin_max

    @property
    def kvectors(self):
        # Return actual kvectors
        kvectors = []
        for k, klist in enumerate(self._kvectors):
            kvectors.append([])
            for kvec in klist:
                actual_vec = self.k0 * (numpy.array(kvec) - self._koffset)
                kvectors[-1].append(list(actual_vec))
        return kvectors

    @kvectors.setter    
    def kvectors(self, kvectors):
        # Smallest kvector
        sample = 0
        self.k0 = 2*math.pi/self.trajectory[sample].cell.side

        # Collect kvectors and compute shift
        self._kvectors = []
        shift = 0
        for klist in kvectors:
            self._kvectors.append([])
            for kvec in klist:
                rounded = numpy.rint(kvec / self.k0)
                self._kvectors[-1].append(numpy.array(rounded, dtype=int))
                # Update shift
                shift = min(shift, int(min(rounded)))

        # Shift to make all array indices start from 0
        self._koffset = int(abs(shift)) + 1
        for klist in self._kvectors:
            for i in range(len(klist)):
                klist[i] = tuple(klist[i] + self._koffset)
    
        # Define kgrid
        self.kgrid = []
        for klist in self._kvectors:
            knorm = numpy.mean([_k_norm(kvec, self.k0, self._koffset) for kvec in klist])
            self.kgrid.append(knorm)
            
    def report(self, verbose=False):
        """
        Return a formatted report of the wave-vector grid used to compute
        the correlation function

        The `verbose` option turns on writing of the individuals
        wavectors (also accessible via the `kvectors` property).
        """
        txt = '# k-point, average, std, vectors in shell\n'
        for i, klist in enumerate(self.kvectors):
            knorms = []
            for kvec in klist:
                k_sq = numpy.dot(kvec, kvec)
                knorms.append(math.sqrt(k_sq))
            knorms = numpy.array(knorms)
            txt += "{} {:f} {:f} {}\n".format(self.kgrid[i], knorms.mean(),
                                              knorms.std(),
                                              len(klist))
        if verbose:
            txt += '\n# k-point, k-vector\n'
            for i, klist in enumerate(self.kvectors):
                for kvec in klist:
                    # Reformat numpy array
                    as_str = str(kvec)
                    as_str = as_str.replace(',', '')
                    as_str = as_str.replace('[', '')
                    as_str = as_str.replace(']', '')
                    txt += '{} {}\n'.format(self.kgrid[i], as_str)
        return txt
