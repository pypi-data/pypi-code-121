"""``g_values`` - Routines related to g-values and radiation pressure
The g-value is the the product of the solar flux at the dopler-shifted
emission wavelength and the scattering probability per atom. See
`Killen, R.M. et al., Icarus 209, 75–87, 2009.
<http://dx.doi.org/10.1016/j.icarus.2010.02.018.>`_ for details on calculating
g-values for important species in Mercury's atmosphere.

The radiation acceleration is given by
:math:`a_{rad} = h g/m \lambda`,
where h is Plank's constant, g is the g-value as a function of radial
velocity, m is the mass of the accelerated species, and λ is the wavelength
of the absorbed photon.
"""
import os
import numpy as np
import pandas as pd
import astropy.units as u
from astropy import constants as const
from nexoclom.atomicdata.atomicmass import atomicmass
from nexoclom.math import interpu
from nexoclom import __file__ as basefile
# pylint: disable=no-member

class gValue:
    r"""Class containing g-value vs. velocity for a specified atom and
    transition.

    **Parameters**

    sp
        atomic species

    wavelength
        Wavelength of the transition. Default=None.

    aplanet
        Distance from the Sun. Can be given as an astropy quantity with
        distance units or as a float assumed to be in AU. Default = 1 AU

    **Class Attributes**

    species
        The input species

    wavelength
        The input wavelength

    aplanet
        The input aplanet

    velocity
        Radial velocity deviation relative to the Sun in km/s.
        Positive values indicate
        motion away from the Sun. Given as a numpy array of astropy quantities

    g
        g-value as function of velocity in units 1/s.
    """
    def __init__(self, sp, wavelength, aplanet=1*u.au):
        self.species = sp

        try:
            self.wavelength = wavelength.to(u.AA)
        except:
            self.wavelength = wavelength * u.AA

        try:
            self.aplanet = aplanet.to(u.au)
        except:
            self.aplanet = aplanet * u.au

        gvalue_file = self.gvalue_filename()
        gvalues = pd.read_pickle(gvalue_file)

        gvalue = gvalues[(gvalues.species == sp) &
                         (gvalues.wavelength == wavelength)]

        if len(gvalue) == 0:
            self.velocity = np.array([0., 1.])*u.km/u.s
            self.g = np.array([0., 0.])/u.s
            self.filename = None
            self.reference = None
            print(f'Warning: g-values not found for species = {sp}')
        elif len(gvalue.filename.unique()) == 1:
            self.velocity = gvalue.velocity.values*u.km/u.s
            self.g = (gvalue.gvalue *
                      gvalue.refpoint**2/self.aplanet.value**2).values/u.s
            s = np.argsort(self.velocity)
            self.velocity, self.g = self.velocity[s], self.g[s]
            self.reference = gvalue.reference.unique()[0]
            self.filename = gvalue.filename.unique()[0]
        else:
            print('This should never happen')
            raise ValueError()

    @classmethod
    def gvalue_filename(self):
        return os.path.join(os.path.dirname(basefile), 'data', 'g-values', 
                            'g-values.pkl')


class RadPresConst:
    r"""Class containing radial acceleration vs. velocity for a specified atom.

    **Parameters**

    sp
        atomic species

    aplanet
        Distance from the Sun. Can be given as an astropy quantity with
        distance units or as a float assumed to be in AU. Default = 1 AU

    database
        Database containing solar system information. Default =
        `thesolarsystem` which probably shouldn't be overridden.

    **Class Attributes**

    species
        The input species

    aplanet
        The input distance from the Sun

    velocity
        Radial velocity deviation relative to the Sun in km/s.
        Positive values indicate
        motion away from the Sun. Given as a numpy array of astropy quantities

    accel
        Radial acceleration vs. velocity with units km/s**2.
    """
    def __init__(self, species, aplanet):
        self.species = species
        if isinstance(aplanet, type(1*u.au)):
            self.aplanet = aplanet
        else:
            self.aplanet = aplanet * u.au

        gvalues = pd.read_pickle(gValue.gvalue_filename())

        if species in gvalues.species.values:
            subset = gvalues.loc[gvalues.species == species]
            self.wavelength = np.array(sorted(subset.wavelength.unique())) * u.AA
            self.velocity = np.array(sorted(subset.velocity.unique())) * u.km/u.s

            # Interpolate gvalues to full velocity set and compute rad pres
            rpres = np.zeros_like(self.velocity)/u.s
            for wave in self.wavelength:
                gval = gValue(species, wave, aplanet)
                g_ = interpu(self.velocity, gval.velocity, gval.g)
                rpres_ = const.h/atomicmass(species)/wave * g_
                rpres += rpres_.to(u.km/u.s**2)
                
            self.accel = rpres
        else:
            self.velocity = np.array([0., 1.])*u.km/u.s
            self.accel = np.array([0., 0.])*u.km/u.s**2
            print(f'Warning: g-values not found for species = {species}')