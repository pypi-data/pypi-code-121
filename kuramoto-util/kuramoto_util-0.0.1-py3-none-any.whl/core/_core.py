import time
import threading
import sys
import warnings
from pprint import pprint
import tqdm
from typing import List, Optional, overload, Union

import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft2, ifft2, rfft2, irfft2, set_global_backend
import pyfftw

from michael960lib.math import fourier
from michael960lib.common import overrides, experimental, deprecated
from michael960lib.common import ModifyingReadOnlyObjectError, IllegalActionError

from torusgrid.grids import RealGrid2D, ComplexGrid2D, RealGrid1D, ComplexGrid1D, StateFunction
from ..weights import ParametrizedWeight
from ..sampling import DistributionSampling


class KuramotoBase:
    def __init__(self, K: float,
        theta: Union[np.ndarray, DistributionSampling], 
        omega: Union[np.ndarray, DistributionSampling], 
        weight: Union[np.ndarray, ParametrizedWeight]):

        self.K = K
        
        self._thetaobj = None
        self.theta_params = dict()
        if isinstance(theta, np.ndarray):
            self.theta = theta
        elif isinstance(theta, DistributionSampling):
            self.theta = theta.get_val()
            self.theta_params = theta.get_params()
            self._thetaobj = theta
        else:
            raise ValueError('invalid theta')

        self._omegaobj = None
        self.omega_params = dict()
        if isinstance(omega, np.ndarray):
            self.omega = omega
        elif isinstance(omega, DistributionSampling):
            self.omega = omega.get_val()
            self.omega_params = omega.get_params()
            self._omegaobj = omega
        else:
            raise ValueError('invalid omega')

        self._weightobj = None
        self.weight_params = dict()
        if isinstance(weight, np.ndarray):
            self.weight = weight
        elif isinstance(weight, ParametrizedWeight):
            self.weight = weight.get_weight()
            self.weight_params = weight.get_params()
            self._weightobj = weight
        else:
            raise ValueError('invalid weight')

        try:
            assert self.theta.shape == self.omega.shape
            assert self.theta.shape == self.weight.shape
        except AssertionError:
            raise ValueError(
            f'theta, omega, and weight have incompatible shapes: {theta.shape}, {omega.shape}, and {weight.shape}')

        self.shape = self.theta.shape
        self.rank = len(self.shape)

    def get_theta_label(self):
        if self._thetaobj is None:
            return 'custom'
        else:
            return self._thetaobj.get_label()

    def get_omega_label(self):
        if self._thetaobj is None:
            return 'custom'
        else:
            return self._omegaobj.get_label()

    def get_weight_label(self):
        if self._weightobj is None:
            return 'custom'
        else:
            return self._weightobj.get_label()



        

class KuramotoStateFunction(StateFunction):
    @overload
    def __init__(self, theta: np.ndarray): ...
    @overload
    def __init__(self, R: float, phi: float): ...
    @overload
    def __init__(self, Z: complex): ...
    def __init__(self, arg1, arg2=None):
        super().__init__()
        if type(arg1) is np.ndarray and arg2 is None:
            Z = np.mean(np.exp(1j*arg1))
            R = np.abs(Z)
            phi = np.angle(Z)

        elif type(arg1) is complex and arg2 is None:
            R = np.abs(Z)
            phi = np.angle(Z)

        elif type(arg1) is float and type(arg2) is float:
            R = arg1 
            phi = arg2 
        else:
            raise ValueError
        self.R = self._content['R'] = R
        self.phi = self._content['phi'] = phi





