import os
import numpy as np
from copy import copy
from functools import wraps
from types import SimpleNamespace

## NOTE: SEE BELOW FOR OPTIONAL DEPENDENCY IMPORTS

from . import logger


class Omega(SimpleNamespace):
    def copy(self, **kwargs):
        omega = copy(self)
        for k, v in kwargs.items():
            setattr(omega, k, v)
        return omega


def _attrrepr(obj):
    return ', '.join(['{}={}'.format(k, getattr(obj, k)) for k in ['h', 'om', 'ol']])


# default cosmological parameters
# From Planck2015, Table IV
OMEGA = Omega()
OMEGA.h  = 67.9
OMEGA.om = 0.3065
OMEGA.ol = 0.6935
OMEGA.ok = 1.0 - OMEGA.om - OMEGA.ol
OMEGA.w0 = -1.0
OMEGA.w1 = 0.0
OMEGA.w2 = 0.0


class CosmologyBase:
    """Simple cosmology class

    """

    __slots__ = ['_omaga']

    def __init__(self, **omega):
        """keyword arguments override the default cosmological parameters:

        """
        self._omega = OMEGA.copy(**omega)
    __init__.__doc__ += _attrrepr(OMEGA)

    def __repr__(self):
        return '<{}: {}>'.format(
            type(self).__name__,
            _attrrepr(self._omega),
            repr(self._omega),
        )

    def __getattr__(self, name):
        """return cosmological parameter value"""
        return getattr(self._omega, name)

    @property
    def omega(self):
        """dictionary of cosmological parameters"""
        return self._omega.__dict__

    def luminosity_distance(self, z):
        """luminosity distance for redshift in Mpc"""
        if np.isscalar(z):
            return float(self._luminosity_distance(z))
        else:
            return np.vectorize(self._luminosity_distance)(z)

    def differential_comoving_volume(self, z):
        """differential comoving volume at redshift in Mpc**3"""
        pass


class CosmologyLAL(CosmologyBase):
    """Simple cosmology class, LAL version

    """
    __slots__ = ['_omega', '_lalomega']

    @wraps(CosmologyBase.__init__)
    def __init__(self, **omega):
        super().__init__(**omega)
        self._lalomega = lal.CreateCosmologicalParametersAndRate().omega
        lal.SetCosmologicalParametersDefaultValue(self._lalomega)
        lalomega = OMEGA.copy(**omega)
        lalomega.h /= 100
        for k, v in lalomega.__dict__.items():
            setattr(self._lalomega, k, v)

    def _luminosity_distance(self, z):
        return lal.LuminosityDistance(self._lalomega, float(z))

    @wraps(CosmologyBase.differential_comoving_volume)
    def differential_comoving_volume(self, z):
        return lal.UniformComovingVolumeDensity(z, self._lalomega)


class CosmologyAstropy(CosmologyBase):
    """Simple cosmology class, astropy version

    """
    __slots__ = ['_omega', 'cosmo']

    @wraps(CosmologyBase.__init__)
    def __init__(self, **omega):
        super().__init__(**omega)
        self.cosmo = cosmology.FlatLambdaCDM(self.h, self.om)

    def _luminosity_distance(self, z):
        return float(self.cosmo.luminosity_distance(z).to(units.Mpc).value)

    @wraps(CosmologyBase.differential_comoving_volume)
    def differential_comoving_volume(self, z):
        return (4.0 * np.pi * units.sr * self.cosmo.differential_comoving_volume(z) / (1.0 + z)).to(units.Mpc**3).value

####################
# IMPORTS
#
# this is done here below the code so that the Cosmology class can be
# specified based on the available libraries

def _use(lib):
    return os.getenv('USE', '').lower() == lib

try:
    import lal
    Cosmology = CosmologyLAL
except ImportError:
    if _use('lal'):
        raise
    try:
        import astropy
        from astropy import cosmology, units
        Cosmology = CosmologyAstropy
    except ImportError:
        if _use('astropy'):
            raise ImportError("Could not import either LAL or astropy.")
    logger.warning("Using 'astropy' for cosmological calculations.  Install the 'lal' package for better performance.")

####################

if __name__ == '__main__':
    from timeit import timeit

    zs = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]

    def run(cmd):
        out = eval(cmd)
        t = timeit(cmd, number=1000, globals=globals())
        return out, t

    def pdiff(a, b):
        return ((a - b) / max(a, b)) * 100

    cosmoLAL = CosmologyLAL()
    cosmoAstropy = CosmologyAstropy()

    fmt = '{:<10}{:<30}{:<30}{:<30}{:<30}'

    print(fmt.format('z', 'dL (lal)', 'dL (astropy)', '% diff', 't_astropy/t_lal'))
    for z in zs:
        dL_lal, t_lal = run('cosmoLAL.luminosity_distance(z)')
        dL_astropy, t_astropy = run('cosmoAstropy.luminosity_distance(z)')
        dd = pdiff(dL_lal, dL_astropy)
        print(fmt.format(z, dL_lal, dL_astropy, dd, t_astropy/t_lal))

    print()

    print(fmt.format('z', 'dV (lal)', 'dV (astropy)', '% diff', 't_astropy/t_lal'))
    for z in zs:
        dV_lal, t_lal = run('cosmoLAL.differential_comoving_volume(z)')
        dV_astropy, t_astropy = run('cosmoAstropy.differential_comoving_volume(z)')
        dd = pdiff(dV_lal, dV_astropy)
        print(fmt.format(z, dV_lal, dV_astropy, dd, t_astropy/t_lal))
