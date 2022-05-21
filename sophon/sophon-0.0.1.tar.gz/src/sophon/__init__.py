'''
Sophon Python module loader
'''
import sys

if sys.version_info < (3,):
    raise Exception("Python 2 has reached end-of-life and is no longer supported by Sophon.")

from .version import __version__