import numpy as np

from .utils import *

def clock(d):
    r"""
    The clock operator $\hat{Z}$ for dimension $d$.
    """
    w = np.exp(2*np.pi*1j/d)
    return np.diag([w**i for i in range(d)])

def shift(d):
    r"""
    The shift operator $\hat{X}$ for dimension $d$.
    """
    return sum([np.outer(basis(d, i+1), basis(d, i))\
                    if i != d-1 else np.outer(basis(d, 0),basis(d, i))\
                        for i in range(d) for j in range(d)])/d

def displace(d, a, b):
    r"""
    The displacement operator $\hat{D}_{a,b} = (-e^{\frac{i\pi}{d}})^{ab}\hat{X}^{b}\hat{Z}^{a}$ for dimension $d$.
    """
    Z, X = clock(d), shift(d)
    return (-np.exp(1j*np.pi/d))**(a*b)*np.linalg.matrix_power(X,b) @ np.linalg.matrix_power(Z,a)

def displacement_operators(d):
    r"""
    Returns a dictionary associating $(a, b)$ with $\hat{D}_{a,b}$ for $a, b \in [0, d)$.
    """
    return np.array([displace(d, a, b) for a in range(d) for b in range(d)])

def weyl_heisenberg_frame(fiducial):
    r"""
    Applies the $d^2$ displacement operators to a fiducial ket.
    """
    d = fiducial.shape[0]
    D = displacement_operators(d)
    return (D @ fiducial).T.reshape(d, d**2)/np.sqrt(d)

def weyl_heisenberg_povm(fiducial):
    r"""
    Generates a Weyl-Heisenberg POVM by applying the $d^2$ displacement operators to a
    fiducial state and then, if the fiducial state is a ket $\mid \psi \rangle$, forming the projector $\mid \psi \rangle \langle \psi \mid$, and normalizing by $\frac{1}{d}$.

    Note that if the fiducial state is a density matrix, it may be the case that it is invariant under some displacement operators, in which case you'll run into problems!
    """
    if fiducial.shape[1] != 1:
        d = fiducial.shape[0]
        D = displacement_operators(d)
        return np.array([D[(a,b)] @ fiducial @ D[(a,b)].conj().T for a in range(d) for b in range(d)])/fiducial.shape[0]
    else:
        return frame_povm(weyl_heisenberg_frame(fiducial))/fiducial.shape[0]
