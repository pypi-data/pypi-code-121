"""Gravitational wave detector inspiral range calculations

The package includes multiple functions for calculating various range
measures for a given PSD.

Analytical methods:

* sensemon_range
* int73

Cosmologically-corrected measures:

* horizon:  (Mpc)
* horizon_redshift (z)
* volume (Mpc^3)
* range (Mpc)
* response_frac (Mpc)
* response_frac_redshift (z)
* reach_frac (Mpc)
* reach_frac_redshift (z)

By default, all functions calculate measures for 1.4/1.4 M_sol BNS
inspirals:

    >>> import inspiral_range
    >>> freq, psd = np.loadtxt('PSD.txt')
    >>> range_bns = inspiral_range.range(freq, psd)

Other masses can be calculated as well:

    >>> range_bbh = inspiral_range.range(freq, psd, m1=30, m2=30)

A convenience function, `cosmological_ranges`, is also included that
calculates various common cosmological measures together in an
efficient way (all return values in Mpc):

* horizonn
* range
* response_50
* response_10
* reach_50
* reach_90

e.g.:

    >>> ranges = inspiral_range.cosmological_ranges(freq, psd)

When calculating multiple measures together it is more efficient to
generate the fiducial waveform first and then pass it to the various
functions:

    >>> H = inspiral_range.CBCWaveform(freq, m1=30, m2=30)
    >>> horizon = inspiral_range.horizon(freq, psd, H=H)
    >>> range = inspiral_range.range(freq, psd, H=H)

See the following references for more information:

   https://dcc.ligo.org/LIGO-P1600071
   https://dcc.ligo.org/LIGO-T1500491
   https://dcc.ligo.org/LIGO-T1100338
   https://dcc.ligo.org/LIGO-T030276

"""

import logging
logger = logging.getLogger('inspiral_range')

try:
    from .__version__ import version as __version__
except ModuleNotFoundError:
    try:
        import setuptools_scm
        __version__ = setuptools_scm.get_version(fallback_version='?.?.?')
    # FIXME: fallback_version is not available in the buster version
    # (3.2.0-1)
    except TypeError:
        __version__ = setuptools_scm.get_version()
    except LookupError:
        __version__ = '?.?.?'
from .inspiral_range import *
from .cosmology import Cosmology
from .waveform import CBCWaveform

__all__ = [
    'int73',
    'sensemon_range',
    'sensemon_horizon',
    'horizon_redshift',
    'horizon',
    'volume',
    'range',
    'response_frac_redshift',
    'response_frac',
    'reach_frac_redshift',
    'reach_frac',
    'cosmological_ranges',
    'Cosmology',
    'CBCWaveform',
]
