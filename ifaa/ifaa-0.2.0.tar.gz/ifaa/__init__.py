import pkg_resources

from .source import IFAA
from .loadData import load_dataM, load_dataC

__version__ = pkg_resources.get_distribution("ifaa").version
__author__ = 'Shangchen Song'
__all__ = ['IFAA', 'load_dataM', 'load_dataC']