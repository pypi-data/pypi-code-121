import logging
from typing import List

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

try:
    from pyabc.distance import Distance
except ImportError:
    logger.error("pyabc must be installed.")


class KolmogorovSmirnovDistance(Distance):
    """
    Compute a 2 sample Kolmogorov Smirnov distance from the
    simulated and observed data.
    """

    def __init__(self, keys: List = None):
        self.keys = keys

    def __call__(self, x: dict, x_0: dict, t: int = None, par: dict = None):
        if self.keys is not None:
            keys = self.keys
        else:
            keys = list(x_0.keys())

        sim_vals = []
        obs_vals = []
        for key in keys:
            sim_vals.append(x[key])
            obs_vals.append(x_0[key])

        sim_vals = np.array(sim_vals).flatten()
        obs_vals = np.array(obs_vals).flatten()

        res = stats.ks_2samp(sim_vals, obs_vals)
        return res.statistic
