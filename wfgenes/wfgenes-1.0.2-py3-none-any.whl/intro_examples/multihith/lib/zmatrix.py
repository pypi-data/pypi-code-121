"""
Methods to manipulate Z-matrices. Example for a Z-matrix:
[
    {
        'label': 'c1',
        'symbol': 'c'
    },
    {
        'label': 'h1',
        'symbol': 'h',
        'distance': {'reference': 'c1', 'value': 1.3, 'constant': False}
    },
    {
        'label': 'h2',
        'symbol': 'h',
        'distance': {'reference': 'c1', 'value': 1.3},
        'angle': {'reference': 'h1', 'value': 120.0}
    },
    {
        'label': 'h3',
        'symbol': 'h',
        'distance': {'reference': 'c1', 'value': 1.3},
        'angle': {'reference': 'h2', 'value': 120.0},
        'dihedral': {'reference': 'h1', 'value': 180.0, 'constant': True}
    }
]
"""
import numpy as np
from numpy import pi, sin, cos, arccos, sqrt
from ase import Atoms
from ase.data import chemical_symbols

@classmethod
def from_zmat(cls, *args, **kwargs):
    dct = zmat2cart(*args, **kwargs)
    dct['constraint'] = zmat2constr(*args)
    return cls(**dct)

Atoms.from_zmat = from_zmat

def zmat2cart(zmat, positions=None):
    """
    Convert a Z-matrix to Cartesian coordinates
    The Cartesian coordinates of the first three atoms can be supplied in the
    optinal 'positions' parameter. Otherwise the first atom will be at the
    origin, the second atom displaced in z direction, and the third atom
    constrained in the yz-plane. For all remaining atoms the algorithm from
    C. R. Eddy, J. Chem. Phys. 38, 1032 (1963) is used.
    """

    labels = {atom['label']: index for index, atom in enumerate(zmat)}
    symbols = [atom['symbol'].capitalize() for atom in zmat]
    assert len(labels) == len(zmat), 'repeated label'
    assert all(s in chemical_symbols for s in symbols), 'unknown symbol'

    if positions is None:
        positions = [[0., 0., 0.]]
        if len(zmat) == 1:
            return {'symbols': symbols, 'positions': positions}
        stre1 = zmat[1]['distance']['value']
        positions.append([0., 0., stre1])
        if len(zmat) == 2:
            return {'symbols': symbols, 'positions': positions}
        stre2 = zmat[2]['distance']['value']
        bend2 = zmat[2]['angle']['value']*pi/180.0
        if labels[zmat[2]['distance']['reference']] == 1:
            assert labels[zmat[2]['angle']['reference']] == 0
            posy = stre2*sin(bend2)
            posz = stre1-stre2*cos(bend2)
        else:
            assert labels[zmat[2]['distance']['reference']] == 0
            assert labels[zmat[2]['angle']['reference']] == 1
            posz = stre2*cos(bend2)
            posy = sqrt(stre2**2-posz**2)
        positions.append([0., posy, posz])

    for zline in zmat[3:]:
        A = labels[zline['dihedral']['reference']]
        B = labels[zline['angle']['reference']]
        C = labels[zline['distance']['reference']]
        alpha = np.array(positions[B])-np.array(positions[A])
        beta = np.array(positions[C])-np.array(positions[B])
        alpha = alpha/np.linalg.norm(alpha)
        beta = beta/np.linalg.norm(beta)
        lambd = [(alpha[(j+1)%3]*beta[(j+2)%3]-beta[(j+1)%3]*alpha[(j+2)%3])
                 /sin(arccos(np.dot(alpha, beta))) for j in range(3)]
        multiplier1 = cos(pi-zline['dihedral']['value']*pi/180.0)
        multiplier2 = sin(pi-zline['dihedral']['value']*pi/180.0)
        mu = [lambd[j]*multiplier1
              +(lambd[(j+1)%3]*beta[(j+2)%3]-beta[(j+1)%3]*lambd[(j+2)%3])
              *multiplier2 for j in range(3)]
        multiplier1 = cos(pi-zline['angle']['value']*pi/180.0)
        multiplier2 = sin(pi-zline['angle']['value']*pi/180.0)
        gamma = [beta[j]*multiplier1
                 +(beta[(j+1)%3]*mu[(j+2)%3]-mu[(j+1)%3]*beta[(j+2)%3])
                 *multiplier2 for j in range(3)]
        pos = [positions[C][j]+zline['distance']['value']*gamma[j] for j in range(3)]
        positions.append(pos)

    return {'symbols': symbols, 'positions': positions}


def zmat2constr(zmat):
    """ Construct ASE constraint object from a Z-matrix """
    from ase.constraints import FixInternals
    labels = {zl['label']: zln for zln, zl in enumerate(zmat)}
    assert len(labels) == len(zmat), 'repeated label'
    bconstr = []
    aconstr = []
    dconstr = []
    for zln, zl in enumerate(zmat):
        if 'distance' in zl:
            disref = labels[zl['distance']['reference']]
            disval = zl['distance']['value']
            if zl['distance'].get('constant', False):
                bind = [disref, zln]
                bconstr.append([disval, bind])
        if 'angle' in zl:
            angref = labels[zl['angle']['reference']]
            angval = zl['angle']['value']
            if zl['angle'].get('constant', False):
                aind = [angref, disref, zln]
                aconstr.append([angval*pi/180., aind])
        if 'dihedral' in zl:
            dihref = labels[zl['dihedral']['reference']]
            dihval = zl['dihedral']['value']
            if zl['dihedral'].get('constant', False):
                dind = [dihref, angref, disref, zln]
                dconstr.append([dihval*pi/180., dind])

    if len(bconstr)+len(aconstr)+len(dconstr):
        return FixInternals(bonds=bconstr, angles=aconstr, dihedrals=dconstr)
