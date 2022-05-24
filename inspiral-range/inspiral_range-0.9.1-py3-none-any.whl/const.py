import scipy.constants

try:
    from lal import MSUN_SI, PC_SI
except ImportError:
    from astropy import constants, units
    MSUN_SI = constants.M_sun.value
    PC_SI = units.parsec.to('m')

c = scipy.constants.c
G = scipy.constants.G
