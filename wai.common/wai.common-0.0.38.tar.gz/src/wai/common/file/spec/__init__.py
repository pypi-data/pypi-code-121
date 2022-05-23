"""
Package for reading in .spec files.

Typical usage:
from wai.common.file import spec

for spectrum in spec.reader('filename.spec'):
    process_spectrum(spectrum)

OR

spectra = spec.read_all('filename.spec')
"""
from ._Field import Field, DATATYPE_BOOLEAN, DATATYPE_NUMERIC, DATATYPE_STRING, DATATYPE_UNKNOWN
from ._Report import Report, NO_ID
from ._SpecFileReader import read_all, reader
from ._Spectrum import Spectrum
from ._SpectrumPoint import SpectrumPoint
