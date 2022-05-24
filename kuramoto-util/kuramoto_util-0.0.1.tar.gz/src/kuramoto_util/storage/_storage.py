import time
import threading
import sys
import warnings
from pprint import pprint
import tqdm
from typing import List, Optional
from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
from scipy.fft import fft2, ifft2, rfft2, irfft2, set_global_backend, fft, ifft
import pyfftw
import h5py

from michael960lib.math import fourier
from michael960lib.common import overrides, experimental, deprecated
from michael960lib.common import ModifyingReadOnlyObjectError, IllegalActionError 
from torusgrid.grids import RealGrid2D, ComplexGrid2D, RealGrid1D, ComplexGrid1D
from torusgrid.dynamics import FancyEvolver, EvolverHistory, StateFunction

from ..core import KuramotoStateFunction, KuramotoBase


class KuramotoWriter:
    def __init__(self, fname: str, kura: KuramotoBase, initial_age=0):
        self.fname = fname
        self.kura = kura
        self.file = h5py.File(fname, 'w')

        self.file.create_dataset('omega', dtype='f', data=kura.omega.tolist())
        for key in kura.omega_params:
            self.file['omega'].attrs[key] = kura.omega_params[key]

        self.file.create_dataset('weight', dtype='f', data=kura.weight.tolist())
        for key in kura.weight_params:
            self.file['weight'].attrs[key] = kura.weight_params[key]

        self.file.create_dataset('theta', dtype='f', data=[kura.theta.tolist()], 
                chunks=(1, *kura.shape), maxshape=(None, *kura.shape))
        for key in kura.theta_params:
            self.file['theta'].attrs[key] = kura.theta_params[key]


        self.file.create_dataset('shape', dtype='i8', data=list(kura.shape))
        self.file.attrs['K'] = kura.K
        self.time = datetime.now()
        self.file.attrs['time'] = self.time.strftime('%Y.%m.%d-%H:%m:%S')
        self.file.create_dataset('t', dtype='f', data=[initial_age], chunks=(1,), maxshape=(None,))
        self._chunk_ind = 0

    def set_datetime_format(self, fmt='%Y.%m.%d-%H:%m:%S'):
        self.file.attrs['time'] = self.time.strftime(fmt)

    def append(self, t: float, theta: np.ndarray):
        self._chunk_ind += 1
        self.file['theta'].resize(self._chunk_ind+1, axis=0)
        self.file['theta'][self._chunk_ind] = theta.tolist()
        self.file['t'].resize(self._chunk_ind+1, axis=0)
        self.file['t'][self._chunk_ind] = t

    def get_file(self):
        return self.file
    
    def check_well_formed(self): 
        r = True
        return r

    def close(self):
        self.file.close()

class KuramotoReader:
    def __init__(self, fname: str):
        self.fname = fname
        self.file = h5py.File(fname, 'r')

        self.K = self.file.attrs['K']
        self.shape = np.array(self.file['shape'])

        self.theta_params = dict(self.file['theta'].attrs)
        self.theta = self.file['theta']
        self.theta_seed = self.theta_params.get('seed', '?')

        self.omega_params = dict(self.file['omega'].attrs)
        self.omega = np.array(self.file['omega'])
        self.omega_dist = self.omega_params.get('type', '?')
        self.omega0 = self.omega_params.get('mean', np.NAN)
        self.gamma = self.omega_params.get('scale', np.NaN)
        self.omega_seed = self.omega_params.get('seed', '?')

        self.weight_params = dict(self.file['weight'].attrs)
        self.weight = np.array(self.file['weight'])
        self.nu = self.weight_params.get('nu', np.NaN)
        self.weight_type = self.weight_params.get('type', '?')

        self.t = np.array(self.file['t'])
        self.Nt = len(self.t)
        self.t_max = self.t[-1]

        self.dt = self.file.attrs['dt']

        self.datetime = self.file.attrs.get('time', '?')

    def get_dimensions(self):
        return len(self.shape)



