"""The definition of Black Sorcery
This module provides the stupidest fixes that are ment to be used *if and only if* there are no other sound workarounds.

Deep down in my heart, I kinna like them tho,
George Vasiliadis
"""

from contextlib import contextmanager

from CleanEmonBackend import NILM_INFERENCE_APIS_DIR


@contextmanager
def nilm_path_fix(nilm_path=NILM_INFERENCE_APIS_DIR):
    """NILM-Inference-APIs is ment to be run as a standalone set of scripts and not as a module (e.g. absence of
    relative imports). In order to integrate it in other packages and/or modules, one must always change manually the
    execution directory and the system path back and forth. This context manager ensures that this operation is done
    consistently.

    Example of use:
    >>> with nilm_path_fix(NILM_INFERENCE_APIS_PATH):
    >>>     # We are virtually executing code from within NILM-Inference-APIs directory
    >>>     function_that_does_nilm_related_stuff()
    >>> # We are back to normal namespace and paths-state
    """

    import os
    import sys
    _original_cwd = os.getcwd()
    _original_path = sys.path.copy()

    os.chdir(nilm_path)
    sys.path.append(nilm_path)
    yield

    os.chdir(_original_cwd)
    sys.path = _original_path
