"""``photolossrates`` - Determine photoionization and photodissociation rates"""
import os
import pandas as pd
import astropy.units as u
from nexoclom import __file__ as basefile


class PhotoRate:
    r"""Determine photoreactions and photorates for a species.

    **Parameters**

    species
        Species to compute rates for.

    aplanet
        Distance from the Sun. Default is 1 AU. Given as either a numeric
        type or an astropy quantity with length units.

    **Class Attributes**

    species
        Species

    aplanet
        Distance from the Sun; astropy quantity with units AU

    rate
        Reaction rate; astropy quantity with units s^{-1}. Rate is the sum
        of all possible reactions for the species.

    reactions
        Pandas dataframe with columns for reaction and rate (in s^{-1}) for
        each reaction for the species. This can be used to determine the
        products produced by photolysis and photoionization.
        
    **Example**
    ::
        >>> from nexoclom.atomicdata import PhotoRate
        >>> kappa = PhotoRate('Na', 0.33)
        >>> print(kappa)
        Species = Na
        Distance = 0.33 AU
        Rate = 6.666666666666666e-05 1 / s
        >>> print(kappa.rate)
        6.666666666666666e-05 1 / s
        >>> print(kappa.reactions)
                       reaction                  kappa
        0  Na, photon -> Na+, e  6.666666666666666e-05
        >>> kappa = PhotoRate('H_2O')
        >>> print(kappa)
        Species = H_2O
        Distance = 1.0 AU
        Rate = 1.2056349999999999e-05 1 / s
        >>> print(kappa.reactions)
                             reaction     kappa
        0      H_2O, photon -> H_2, O  5.97e-07
        1       H_2O, photon -> OH, H  1.03e-05
        2     H_2O, photon -> H, H, O  7.54e-07
        3   H_2O, photon -> H, OH+, e  5.54e-08
        4   H_2O, photon -> OH, H+, e  1.31e-08
        5    H_2O, photon -> H_2O+, e  3.31e-07
        6  H_2O, photon -> H_2, O+, e  5.85e-09

    """
    def __init__(self, species, aplanet_=1.*u.AU):
        photorates = pd.read_pickle(self.photorates_filename())
        prates = photorates[photorates.species == species]

        if isinstance(aplanet_, type(1*u.au)):
            aplanet = aplanet_.value
        else:
            aplanet = aplanet_

        self.species = species
        self.aplanet = aplanet*u.au

        # Photo rate adjusted to proper heliocentric distance
        if len(prates) == 0:
            print('No photoreactions found')
            self.reactions = None
            self.rate = 1e-30/u.s
        else:
            rates = prates['kappa'].apply(lambda k: k/aplanet**2).values
            self.reactions = prates
            self.rate = rates.sum()/u.s

    def __str__(self):
        output = (f'Species = {self.species}\n'
                  f'Distance = {self.aplanet}\n'
                  f'Rate = {self.rate}')
        return output

    def photorates_filename(self):
        basepath = os.path.dirname(basefile)
        return os.path.join(basepath, 'data', 'Loss', 'photorates.pkl')
        
