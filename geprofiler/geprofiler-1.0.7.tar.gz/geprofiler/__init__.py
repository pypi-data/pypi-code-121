import warnings

from geprofiler.profiler import Profiler

__version__ = "1.0.0"

# enable deprecation warnings
warnings.filterwarnings("once", ".*", DeprecationWarning, r"geprofiler\..*")


def load_ipython_extension(ipython):
    """
    This function is called by IPython to load the geprofiler IPython
    extension, which is done with the magic command `%load_ext geprofiler`.
    """

    from geprofiler.magic import GeprofilerMagic

    ipython.register_magics(GeprofilerMagic)
