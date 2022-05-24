import numpy as np


def coulomb(atoms, op):
    '''
        All-electron Coulomb potential.
        Latex: Eq. 3.15 ff.
               List. 3.17
    '''
    with np.errstate(divide='ignore', invalid='ignore'):
        Vcoul = -4 * np.pi * atoms.Z[0] / atoms.G2
    Vcoul[0] = 0
    return op.J(Vcoul * atoms.Sf)
