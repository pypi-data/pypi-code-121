# ensure correct os
import platform

if platform.system() not in ['Linux', 'Windows']:
	raise OSError('lpi_andor can only be run on Linux or Windows.')

# TODO: Remove if .so files are added
if platform.system() == 'Linux':
	raise OSError('lpi_andor can not run on Linux because the required .so library files are not included in package.')

# import resources
from ._version import __version__
from .spectrometer import Spectrometer
