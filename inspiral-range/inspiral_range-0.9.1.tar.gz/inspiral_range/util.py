from __future__ import division
import numpy as np


def lalfs_get_data(lalfs):
    """Return frequency and data arrays from LAL FrequencySeries

    @returns (freq, data) tuple of numpy.arrays

    """
    freq = lalfs.f0 + np.arange(len(lalfs.data.data)) * lalfs.deltaF
    data = lalfs.data.data
    return freq, data


def v2r(v):
    """Sphere radius for given volume"""
    return float(3.0 * v / 4.0 / np.pi)**(1.0/3.0)


def r2v(r):
    """Sphere volume for given radius"""
    return float(4.0/3.0 * np.pi * r**3.0)
