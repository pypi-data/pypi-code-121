import os
import math
import tempfile
from typing import Union

# midi / note / freq lookup


def frange(start, stop, by, sig_digits=5):
    """
    Generate a range of float values.
    """
    div = math.pow(10, sig_digits)
    for value in range(int(start * div), int(stop * div), int(by * div)):
        yield round(value / div, sig_digits)


def here(f, *args):
    """
    Pass __file__ to get the current directory and *args to generate a filepath
    """
    return os.path.join(os.path.dirname(os.path.abspath(f)), *args)


def make_tempfile(format: str = "txt"):
    """
    Make a tempfile
    """
    return tempfile.mkstemp(suffix=f".{format}")[-1]


def bpm_to_time(
    bpm: float = 120.00, count: Union[str, int, float] = 1, timesig: str = "4/4"
):
    """
    Take a bpm, note count, and timesig and return a length in seconds
    """
    if isinstance(count, str):
        if "/" in count:
            numerator, denominator = count.split("/")
            count = float(numerator) / float(denominator)
    time_segs = timesig.split("/")
    return (60.00 / float(bpm)) * float(time_segs[0]) * float(count) * 1000.0


def rescale(x, range_x, range_y, sig_digits=3):

    # Figure out how 'wide' each range is
    x_span = max(range_x) - min(range_x)
    y_span = max(range_y) - min(range_y)

    # Compute the scale factor between left and right values
    scale_factor = float(y_span) / float(x_span)

    return round(min(range_y) + (x - min(range_x)) * scale_factor, sig_digits)
