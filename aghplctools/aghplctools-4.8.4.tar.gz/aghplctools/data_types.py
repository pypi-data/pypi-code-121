"""Deprecated. Moved to data.sample"""
import warnings
from .data.sample import DADSignalInfo, HPLCSampleInfo, DADSignal, DADSpectrum, HPLCSample

warnings.warn(  # v4.5.0
    'the data_types module has been moved to data.sample, please update your imports',
    DeprecationWarning,
    stacklevel=2,
)
