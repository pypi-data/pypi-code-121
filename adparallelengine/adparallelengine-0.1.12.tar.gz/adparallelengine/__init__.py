"""A wrapper around several ways of doing map multiprocessing in Python.

One can use :
* Dask
* concurrent.futures
* mpi4py.futures

>>> # TODO
"""

from .adparallelengine import Engine

from . import _version
__version__ = _version.get_versions()['version']
