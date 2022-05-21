import os
import math
import tempfile

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
    return tempfile.mkstemp(suffix=f".{format}")[-1]
