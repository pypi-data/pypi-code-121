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


class DistributionSampling:
    def __init__(self, shape: Tuple[int], seed: int):
        self._params = {'seed': seed}

        self.shape = shape
        self.rank = len(shape)
        self._val = np.zeros(shape)
        self.rng = np.random.default_rng(seed)

        self.label = 'NULL'
    
    def get_val(self):
        return self._val.copy()

    def get_params(self):
        return self._params.copy()

    def get_label(self):
        return self.label


class Uniform(DistributionSampling):
    def __init__(self, shape: Tuple[int], seed: int, low: float, high: float):
        super().__init__(shape, seed)
        self._val = self.rng.uniform(low, high, size=shape)
        self._params['low'] = low
        self._params['high'] = high
        self._params['type'] = 'uniform'
        self.label = f'uniform {low:.3f}~{high:.3f}'


class Lorentzian(DistributionSampling):
    def __init__(self, shape: Tuple[int], seed: int, mean: float, scale: float):
        super().__init__(shape, seed)
        self._val = self.rng.standard_cauchy(size=shape) * scale + mean
        self._params['mean'] = mean
        self._params['scale'] = scale
        self._params['type'] = 'cauchy'
        self.label = f'cauchy({mean:.3f},{scale:.3f})'

class Gaussian(DistributionSampling):
    def __init__(self, shape: Tuple[int], seed: int, mean: float, scale: float):
        super().__init__(shape, seed)
        self._val = self.rng.normal(size=shape) * scale + mean
        self._params['mean'] = mean
        self._params['scale'] = scale
        self._params['type'] = 'normal'
        self.label = f'normal({mean:.3f},{scale:.3f})'



