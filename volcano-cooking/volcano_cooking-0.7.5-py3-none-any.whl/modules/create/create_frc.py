"""Create volcanic forcing as a Poisson process with power law amplitudes."""

from abc import ABC, abstractmethod
from typing import Tuple

import model
import numpy as np
import scipy.stats as scp_stats


class FrcGenerator(ABC):
    @abstractmethod
    def get_frc(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return time and a realisation of the synthetic forcing signal."""


class StdFrc(FrcGenerator):
    def __init__(self, fs: float = 12, total_pulses: int = 300) -> None:
        if total_pulses < 1:
            raise ValueError(f"Can't create empty arrays, {total_pulses} = .")
        self.gamma = 0.1
        self.my_frc = model.StandardForcingGenerator()
        self.my_frc.set_amplitude_distribution(lambda k: self.__lomax_amp(k, 1.8))
        self.times = np.arange(0, (total_pulses + 1) / self.gamma, 1 / fs)

    def __lomax_amp(self, k: int, c: float) -> np.ndarray:
        return scp_stats.lomax.rvs(c, size=k)

    def get_frc(self) -> Tuple[np.ndarray, np.ndarray]:
        frc = self.my_frc.get_forcing(self.times, self.gamma)
        ta, amp = frc.arrival_times, frc.amplitudes
        mask = np.argsort(ta)
        ta[:] = ta[mask]
        amp[:] = amp[mask]
        return ta, amp


class Frc(FrcGenerator):
    def __init__(self, fs: float = 1, size: int = 9999) -> None:
        # Lomax
        self.fs = fs
        self.fpp = model.PointModel(gamma=0.1, total_duration=size, dt=1 / self.fs)
        my_forcing_gen = model.StandardForcingGenerator()
        my_forcing_gen.set_amplitude_distribution(lambda k: self.__lomax_amp(k, 1.8))
        self.fpp.set_custom_forcing_generator(my_forcing_gen)

    def __lomax_amp(self, k: int, c: float) -> np.ndarray:
        return scp_stats.lomax.rvs(c, size=k)

    def get_fpp(self) -> Tuple[np.ndarray, np.ndarray]:
        t, f = self.fpp.make_realization()
        return t, f

    def get_frc(self) -> Tuple[np.ndarray, np.ndarray]:
        self.fpp.make_realization()
        last_frc = self.fpp.get_last_used_forcing()
        ta, amp = last_frc.arrival_times, last_frc.amplitudes
        mask = np.argsort(ta)
        ta[:] = ta[mask]
        amp[:] = amp[mask]
        return ta, amp
