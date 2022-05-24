import numpy as np


class PWBasis:
    '''Basis-set dependent operators for plane waves (PW).'''
    def __init__(self, atoms):
        self.atoms = atoms

    def O(self, W):
        return O(self.atoms, W)

    def L(self, W):
        return L(self.atoms, W)

    def Linv(self, W):
        return Linv(self.atoms, W)

    def I(self, W):
        return I(self.atoms, W)

    def J(self, W):
        return J(self.atoms, W)

    def Idag(self, W):
        return Idag(self.atoms, W)

    def Jdag(self, W):
        return Jdag(self.atoms, W)


def O(atoms, W):
    '''
        Overlap operator.
        Latex: List. 3.9
    '''
    return atoms.Omega * W


def L(atoms, W):
    '''
        Laplacian operator.
        Latex: Eq. 3.10
               List. 3.11
    '''
    if len(W) == len(atoms.G2c):
        G2 = atoms.G2c[:, None]
    else:
        G2 = atoms.G2[:, None]
    return -atoms.Omega * G2 * W


def Linv(atoms, W):
    '''
        Inverse Laplacian operator.
        Latex: List. 3.12
    '''
    out = np.empty_like(W, dtype=complex)
    with np.errstate(divide='ignore', invalid='ignore'):
        if W.ndim == 1:
            out = W / atoms.G2 / -atoms.Omega
            out[0] = 0
        else:
            G2 = atoms.G2[:, None]
            out = W / G2 / -atoms.Omega
            out[0, :] = 0
    return out


def I(atoms, W):
    '''
        Backwards transformation from reciprocal space to real-space.
        Latex: Eq. 3.11
               List. 3.13
    '''
    n = np.prod(atoms.s)
    if len(W) == len(atoms.G2):
        Wfft = W
    else:
        if W.ndim == 1:
            Wfft = np.zeros(n, dtype=complex)
        else:
            Wfft = np.zeros((n, atoms.Ns), dtype=complex)
        Wfft[atoms.active] = W

    if W.ndim == 1:
        Wfft = Wfft.reshape(atoms.s)
        Finv = np.fft.ifftn(Wfft).ravel()
    else:
        Wfft = Wfft.reshape(np.append(atoms.s, atoms.Ns))
        Finv = np.fft.ifftn(Wfft, axes=(0, 1, 2)).reshape((n, atoms.Ns))
    return Finv * n


def J(atoms, W):
    '''
        Forward transformation from real-space to reciprocal space.
        Latex: Eq. 3.12
               List. 3.14
    '''
    n = np.prod(atoms.s)
    if W.ndim == 1:
        Wfft = W.reshape(atoms.s)
        F = np.fft.fftn(Wfft).ravel()
    else:
        Wfft = W.reshape(np.append(atoms.s, atoms.Ns))
        F = np.fft.fftn(Wfft, axes=(0, 1, 2)).reshape((n, atoms.Ns))
    return F / n


def Idag(atoms, W):
    '''
        Conjugated backwards transformation from real-space to reciprocal space.
        Latex: Eq. 3.13
               List. 3.15
    '''
    n = np.prod(atoms.s)
    F = J(atoms, W)
    F = F[atoms.active]
    return F * n


def Jdag(atoms, W):
    '''
        Conjugated forward transformation from reciprocal space to real-space.
        Latex: Eq. 3.14
               List. 3.16
    '''
    n = np.prod(atoms.s)
    Finv = I(atoms, W)
    return Finv / n
