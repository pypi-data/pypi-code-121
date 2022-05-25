import warnings
from .data.time_course import HPLCTarget, plot, stackedplot, find_max_area

warnings.warn(  # v4.5.0
    'the hplc module has been moved to data.time_course, please update your imports',
    DeprecationWarning,
    stacklevel=2,
)
