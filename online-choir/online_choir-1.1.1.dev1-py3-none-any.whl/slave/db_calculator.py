from typing import Optional, Union

import numpy as np

from ..common.constants import SATURATION_LEVEL
from ..common.utils import to_db, to_gain


class DbCalculator:
    """
    Calculates the signal level in dBs.
    By convention, the following levels are defined:
    * 0 dB: the maximum before saturation
    * 10 dB: saturation
    * -100 dB: perfectly silent (but signal present)
    """
    def __init__(self, *, gain: Optional[Union[float, str]] = None, gain_db: Optional[Union[float, str]] = None):
        self.set_gain(gain=gain, gain_db=gain_db)

    def set_gain(self, *, gain: Optional[Union[float, str]] = None, gain_db: Optional[Union[float, str]] = None):
        if gain is not None:
            if gain_db is not None:
                raise ValueError("Cannot specify both gain and gain_db")
            self.gain, self.gain_db = float(gain), to_db(gain)
        elif gain_db is not None:
            self.gain, self.gain_db = to_gain(gain_db), float(gain_db)
        else:
            raise ValueError("Must specify either gain or gain_db")

    def from_sample(self, sample: np.ndarray) -> float:
        peak = np.abs(sample).max()
        if peak * self.gain >= SATURATION_LEVEL:
            return 10.
        var = sample.var()  # signal can clip if var > 0.1111, therefore we set the 0dB to 0.1111.
        if var == 0:
            return -100.
        return 10 * np.log10(9 * var) + self.gain_db

    def from_chunk(self, chunk: bytes) -> float:
        pass
