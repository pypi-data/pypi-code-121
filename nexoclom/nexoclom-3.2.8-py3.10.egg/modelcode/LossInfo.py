import numpy as np
from ..atomicdata import PhotoRate
import astropy.units as u

class LossInfo:
    def __init__(self, atom, lifetime, aplanet):
        # Initialization
        self.photo = 0.
        self.eimp = 0.
        self.chX = 0.
        self.reactions = []
        
        if isinstance(lifetime, type(1*u.s)):
            lifetime_ = lifetime.value
        else:
            lifetime_ = lifetime

        if lifetime_ < 0:
            self.photo = np.abs(1./lifetime_)
            self.reactions = 'Generic photo reaction'
        elif lifetime_ == 0:
            photo = PhotoRate(atom, aplanet)
            self.photo = photo.rate.value
            self.reactions = photo.reactions['reaction'].values

            # Electron impact

            # Charge exchange
        else:
            print('LossInfo objects should not be '
                  'instantiated with lifetime > 0')
            pass

        if len(self.reactions) == 0:
            self.reactions = None

    def __len__(self):
        return len(self.reactions) if self.reactions is not None else 0

    def __str__(self):
        if len(self) == 0:
            return 'No reactions included'
        elif len(self) == 1:
            result = f'Included Reaction: {self.reactions[0]}'
        else:
            reacs = '\n\t'.join(self.reactions)
            result = f'Included Reactions: {reacs}'

        if self.photo != 0:
            result += f'\nPhoto Rate = {self.photo:0.2e} s'
        if self.eimp != 0:
            result += f'\nElectron Impact Rate = {self.eimp:0.2e} UNIT'
        if self.chX!= 0:
            result += f'\nCharge Exchange Rate = {self.chX:0.2e} UNIT'

        return result
