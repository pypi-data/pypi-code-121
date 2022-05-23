import os

__all__ = ["__version__"]

try:
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'VERSION')) as version_file:
        __version__ = version_file.read().strip()
        
except IOError:
    __version__ = 'dev'