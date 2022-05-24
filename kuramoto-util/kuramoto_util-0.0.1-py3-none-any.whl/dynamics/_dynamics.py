import time
import threading
import sys
import warnings
from pprint import pprint
import tqdm
from typing import List, Optional, overload

import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import set_global_backend, fftn
import pyfftw
import h5py

from michael960lib.math import fourier
from michael960lib.common import overrides, experimental, deprecated
from michael960lib.common import ModifyingReadOnlyObjectError, IllegalActionError 
from torusgrid.grids import RealGrid2D, ComplexGrid2D, RealGrid1D, ComplexGrid1D, RealGridND, ComplexGridND
from torusgrid.dynamics import FancyEvolver, EvolverHistory, StateFunction

from ..core import KuramotoStateFunction, KuramotoBase
from ..storage import KuramotoWriter


class KuramotoEvolver(FancyEvolver):
    @overload
    def __init__(self, kura: KuramotoBase, dt: float): ...
    @overload
    def __init__(self, K: float, theta: np.ndarray, omega: np.ndarray, weight: np.ndarray, dt: float): ...
    def __init__(self, *args):
        if len(args) == 2:
            self.kura = args[0]
            self.dt = args[1]
        elif len(args) == 5:
            self.kura = KuramotoBase(args[0], args[1], args[2], args[3])
            self.dt = arg[4]
        else:
            raise ValueError('illegal arguments')

        theta = self.kura.theta.copy()

        self._thetagrid = RealGridND(self.kura.shape)
        self._thetagrid.set_psi(theta)
        self.theta = self._thetagrid.psi
        self.wk = fftn(self.kura.weight)
        self.omega = self.kura.omega.copy()

        super().__init__(self._thetagrid)

        self.Z = ComplexGridND(self.kura.shape)
        self.Z.initialize_fft()

        self.age = 0 
        self.theta_tmp = theta.copy()
        self.name = 'KuramotoND'
    
        self.K = self.kura.K
        self.info = {'system': self.name, 'dt': self.dt, 'K': self.K, 'shape': self.kura.shape,
            'dim': self.kura.rank,
            'omega_dist': self.kura.omega_params.get('type', '?'),
            'omega0': self.kura.omega_params.get('mean', np.nan),
            'gamma': self.kura.omega_params.get('scale', np.nan),
            'weight_type': self.kura.weight_params.get('type', '?'),

            'theta_label': self.kura.get_theta_label(),
            'omega_label': self.kura.get_omega_label(),
            'weight_label': self.kura.get_weight_label()
        }

        self.hdf = None
        self.is_recording = False

        self.set_display_format(
            '[{system}][dim={dim} shape={shape} K={K:5.2f}][weight: {weight_label}]' +\
            '[omega: {omega_label}]' +\
            '[dt={dt:6.3f} t={age:>09.3f}][R={R:4.2f} phi={phi:>5.2f}]'
        )

    def start_recording(self, fname):
        self.hdf = KuramotoWriter(fname, self.kura, self.age)
        self.hdf.file.attrs['dt'] = self.dt
        self.hdf.file.attrs['system'] = self.name
        self.is_recording = True

    def end_recording(self):
        self.hdf.close()

    def theta_dot(self):
        self.Z.psi[...] = np.exp(1j*self.theta_tmp)
        z = np.exp(1j*self.theta_tmp)
        self.Z.fft()
        self.Z.psi_k *= self.wk
        self.Z.ifft() 

        return self.K*np.imag(self.Z.psi/z) + self.omega

    @overrides(FancyEvolver)
    def step(self):
        self.theta_tmp[...] = self.theta
        k0 = self.theta_dot()
        self.theta_tmp[...] = self.theta + self.dt/2 * k0
        k1 = self.theta_dot()
        self.theta_tmp[...] = self.theta + self.dt/2 * k1
        k2 = self.theta_dot()
        self.theta_tmp[...] = self.theta + self.dt * k2
        k3 = self.theta_dot()

        self.theta += self.dt * (k0 + 2*k1 + 2*k2 + k3) / 6
        self.age += self.dt

    @overrides(FancyEvolver)
    def on_epoch_end(self, pb: tqdm.tqdm):
        super().on_epoch_end(pb)
        if self.is_recording:
            self.hdf.append(self.age, self.theta)

    @overrides(FancyEvolver)
    def on_nonstop_epoch_end(self):
        super().on_nonstop_epoch_end()
        if self.is_recording:
            self.hdf.append(self.age, self.theta)

    @overrides(FancyEvolver)
    def get_state_function(self) -> KuramotoStateFunction:
        return KuramotoStateFunction(self.theta)

    @overrides(FancyEvolver)
    def get_evolver_state(self) -> dict():
        _ = {
                'age': self.age
        }
        return _


# class KuramotoEvolver1D(KuramotoEvolver):
    # @overload
    # def __init__(self, kura: KuramotoBase, dt: float): ...
    # @overload
    # def __init__(self, K: float, theta: np.ndarray, omega: np.ndarray, weight: np.ndarray, dt: float): ...
    # def __init__(self, *args):
        # if len(args) == 2:
            # self.kura = args[0]
            # self.dt = args[1]
        # elif len(args) == 5:
            # self.kura = KuramotoBase(args[0], args[1], args[2], args[3])
            # self.dt = arg[4]
        # else:
            # raise ValueError('illegal arguments')

        # try:
            # assert len(self.kura.shape) == 1
        # except AssertionError:
            # raise ValueError('theta, omega, and weight must be one dimensional arrays of the same length')

        # theta = self.kura.theta.copy()
        # N = self.kura.shape[0]

        # self._thetagrid = RealGrid1D(N)
        # self._thetagrid.set_psi(theta)
        # self.theta = self._thetagrid.psi
        # self.wk = fft(self.kura.weight)
        # self.omega = self.kura.omega.copy()

        # super().__init__(self._thetagrid)

        # self.Z = ComplexGrid1D(N)
        # self.Z.initialize_fft()

        # self.age = 0 
        # self.theta_tmp = theta.copy()
        # self.name = 'Kuramoto1D'
    
        # self.K = self.kura.K
        # self.info = {'system': self.name, 'dt': self.dt, 'K': self.K, 'N': N,
            # 'dist': self.kura.omega_params.get('type', '?'),
            # 'omega0': self.kura.omega_params.get('mean', '?'),
            # 'weight': self.kura.weight_params.get('type', '?'),
            # 'nu': self.kura.weight_params.get('nu', '?')
        # }

        # self.hdf = None
        # self.is_recording = False

        # dt = self.dt
        # self.set_display_format(
            # '[{system}][N={N:<5} K={K:5.2f}][weight={weight} nu={nu:3.1f}] ' +\
            # '[dist={dist} omega0={omega0:<4.2f}]' +\
            # '[dt={dt:6.3f} t={age:>09.3f}][R={R:4.2f} phi={phi:>5.2f}]'
        # )

    # def start_recording(self, fname):
        # self.hdf = KuramotoHDF(fname, self.kura, self.age)
        # self.hdf.file.attrs['N'] = self.kura.shape[0]
        # self.hdf.file.attrs['dt'] = self.dt
        # self.hdf.file.attrs['system'] = self.name
        # self.is_recording = True

    # def end_recording(self):
        # self.hdf.close()

    # def theta_dot(self):
        # self.Z.psi[...] = np.exp(1j*self.theta_tmp)
        # z = np.exp(1j*self.theta_tmp)
        # self.Z.fft()
        # self.Z.psi_k *= self.wk
        # self.Z.ifft() 

        # return self.K*np.imag(self.Z.psi/z) + self.omega

    # @overrides(FancyEvolver)
    # def step(self):
        # self.theta_tmp[:] = self.theta
        # k0 = self.theta_dot()
        # self.theta_tmp[:] = self.theta + self.dt/2 * k0
        # k1 = self.theta_dot()
        # self.theta_tmp[:] = self.theta + self.dt/2 * k1
        # k2 = self.theta_dot()
        # self.theta_tmp[:] = self.theta + self.dt * k2
        # k3 = self.theta_dot()

        # self.theta += self.dt * (k0 + 2*k1 + 2*k2 + k3) / 6
        # self.age += self.dt

    # @overrides(FancyEvolver)
    # def on_epoch_end(self, pb: tqdm.tqdm):
        # super().on_epoch_end(pb)
        # if self.is_recording:
            # self.hdf.append(self.age, self.theta)

    # @overrides(FancyEvolver)
    # def on_nonstop_epoch_end(self):
        # super().on_nonstop_epoch_end()
        # if self.is_recording:
            # self.hdf.append(self.age, self.theta)

    # @overrides(FancyEvolver)
    # def get_state_function(self) -> KuramotoStateFunction:
        # return KuramotoStateFunction(self.theta)

    # @overrides(FancyEvolver)
    # def get_evolver_state(self) -> dict():
        # _ = {
                # 'age': self.age
        # }
        # return _



