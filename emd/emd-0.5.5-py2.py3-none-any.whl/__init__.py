"""EMD Package."""

#!/usr/bin/python

# vim: set expandtab ts=4 sw=4:

"""
Package for Empirical Mode Decomposition analyses.

Submodules:
    sift - compute Intrinsic Mode Functions from time-series
    imftools - compute common metrics and operations on IMFs
    spectra - compute frequency transforms and power spectra
    cycles - routines for analysing single cycles
    simulate - create artificial signals for analysis
    plotting - helper functions for producing figures
    logger - tracking analysis progress to the console or logfiles
    support - helpers relating to packaging, checking and errors
    utils - general helpers that don't fit elsewhere

"""

from . import _sift_core  # noqa: F401, F403, I001
from . import support  # noqa: F401, F403, I001
from . import sift  # noqa: F401, F403, I001
from . import spectra  # noqa: F401, F403, I001
from . import _cycles_support  # noqa: F401, F403, I001
from . import cycles  # noqa: F401, F403, I001
from . import imftools  # noqa: F401, F403
from . import logger  # noqa: F401, F403
from . import plotting  # noqa: F401, F403, I001
from . import simulate  # noqa: F401, F403

# Store package version
__version__ = support.get_installed_version()

# Set logger to only show warning/critical messages
logger.set_up(level='WARNING')
