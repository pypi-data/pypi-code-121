"""This loads the generic solar system kernels

Kernels to load:
    * leap second
    * spk for solar system and moons
    * planetary constants
    * frames if available
"""
import spiceypy as spice
import os
import glob

path = '/Users/mburger/Work/Data/spice_kernels/Generic'

# Need to do better than hard code it
def load_kernels():
    ## Determine the path to the spice kernels
    kernels = []

    ## Load the leapseconds (lsk kernel)
    lsk_kernel = glob.glob(os.path.join(path, 'lsk', '*.tls'))
    lsk_kernel = lsk_kernel[-1]
    spice.furnsh(lsk_kernel)
    kernels.append(lsk_kernel)

    ##Generic Solar System ephemeris kernels
    ##  1) load all the planet and satellite kernels
    ##      Note 11/20/2014:
    ##      DE430 is the appropriate planetary kernel for all the planets except Pluto
    ##      DE432 is provided for Pluto

    spk_kernel = ['spk/planets/de430.bsp',
    #  'spk/satellites/mar097.bsp',
      'spk/satellites/jup310.bsp'
    #  'spk/satellites/sat365.bsp',
    #  'spk/satellites/ura111.bsp',
    #  'spk/satellites/nep081.bsp',
    #  'spk/satellites/nep077.bsp',
    #  'spk/satellites/plu043.bsp',
     ]

    for kern in spk_kernel:
        spice.furnsh(os.path.join(path, kern))
        kernels.append(path+kern)

    ## Load the planetary constants (pck kernel)
    pck_kernel = os.path.join(path, 'pck/pck00010.tpc')
    spice.furnsh(pck_kernel)
    kernels.append(pck_kernel)

    ## Load the frames kernels if available
    fk_kernel = ['JEF.tk', 'SEF.tf', 'SMF.tf']
    for kern in fk_kernel:
        kk = os.path.join(path, 'Homemade/fk/', kern)
        if os.path.isfile(kk):
            spice.furnsh(kk)
            kernels.append(kk)

    return kernels
