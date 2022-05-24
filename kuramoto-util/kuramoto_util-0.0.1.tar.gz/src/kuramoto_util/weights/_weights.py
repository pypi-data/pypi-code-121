import time
import threading
import sys
import warnings
from pprint import pprint
import tqdm
from typing import List, Optional, overload, Tuple

import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft2, ifft2, rfft2, irfft2, set_global_backend
import pyfftw

from michael960lib.math import fourier
from michael960lib.common import overrides, experimental, deprecated
from michael960lib.common import ModifyingReadOnlyObjectError, IllegalActionError

from torusgrid.grids import RealGrid2D, ComplexGrid2D, RealGrid1D, ComplexGrid1D, StateFunction

from ..math.math import torus_distance


class ParametrizedWeight:
    def __init__(self, shape: Tuple[int]):
        self._params = dict()
        self.name = 'NULL'
        self.label = 'NULL'
        self.shape = shape
        self.rank = len(shape)
        self._weight = np.zeros(shape)
        self._origin = tuple(0 for i in range(self.rank))


    
    def get_params(self):
        return self._params.copy()

    def get_weight(self):
        return self._weight.copy()

    def get_label(self):
        return self.label



class PowerLaw(ParametrizedWeight):
    def __init__(self, shape: Tuple[int], nu: float):
        super().__init__(shape)
        self._params['nu'] = nu
        self._params['type'] = self.name = 'power'
        self.label = f'power({nu})'

        for k, v in np.ndenumerate(self._weight):
            if k == self._origin:
                self._weight[k] = 0
            else:
                r = torus_distance(self.shape, k)
                self._weight[k] = 1/r**nu
        

class NearestNeighbor(ParametrizedWeight):
    def __init__(self, shape: Tuple[int]):
        super().__init__(shape)
        self._params['type'] = self.name = 'nearest-neighbor'
        for i in range(self.rank):
            p1 = tuple(1 if j==i else 0 for j in range(self.rank))
            p2 = tuple(-1 if j==i else 0 for j in range(self.rank))

            self._weight[p1] = 1
            self._weight[p2] = 1
        self.label = 'nearest'




