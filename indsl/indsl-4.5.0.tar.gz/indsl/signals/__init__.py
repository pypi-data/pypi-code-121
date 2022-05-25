from .generator import const_value, insert_data_gaps, line, perturb_timestamp, sine_wave
from .noise import white_noise
from .polynomial import univariate_polynomial


TOOLBOX_NAME = "Signal generator"

__all__ = [
    "line",
    "perturb_timestamp",
    "insert_data_gaps",
    "sine_wave",
    "white_noise",
    "univariate_polynomial",
    "const_value",
]
