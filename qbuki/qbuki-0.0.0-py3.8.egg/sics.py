import numpy as np
import pkg_resources
from itertools import product

from .weyl_heisenberg import *

def sic_fiducial(d):
    r"""
    Loads a Weyl-Heisenberg covariant SIC-POVM fiducial state of dimension $d$ from the repository provided here: http://www.physics.umb.edu/Research/QBism/solutions.html.
    """
    f = pkg_resources.resource_stream(__name__, "sic_povms/d%d.txt" % d)
    fiducial = []
    for line in f:
        if line.strip() != "":
            re, im = [float(v) for v in line.split()]
            fiducial.append(re + 1j*im)
    return normalize(np.array(fiducial).reshape(d, 1))

def sic_frame(d):
    r"""
    Returns the $d^2$ states constructed by applying the Weyl-Heisenberg displacement operators to the SIC-POVM fiducial state of dimension $d$.
    """
    return weyl_heisenberg_frame(sic_fiducial(d))

def sic_povm(d):
    r"""
    Returns a SIC-POVM of dimension $d$.
    """
    return frame_povm(weyl_heisenberg_frame(sic_fiducial(d)))

def hoggar_sic_fiducial():
    r"""
    Returns a fiducial state for the exceptional SIC in dimension $8$, the Hoggar SIC.

    Unnormalized: $\begin{pmatrix} -1 + 2i \\ 1 \\ 1 \\ 1 \\ 1 \\ 1 \\ 1 \\ 1 \end{pmatrix}$.
    """
    return normalize(np.array([-1 + 2j, 1, 1, 1, 1, 1, 1, 1])).reshape(8, 1)

def hoggar_sic_povm():
    r"""
    Constructs the Hoggar POVM, which is covariant under the tensor product of three copies of the $d=2$ Weyl-Heisenberg group. In other words, we apply the 64 displacement operators:

    $$ \hat{D}_{a, b, c, d, e, f} = X^{a}Z^{b} \otimes X^{c}Z^{d} \otimes X^{e}Z^{f} $$

    to the Hoggar fiducial state, form the corresponding projectors, and rescale by $\frac{1}{8}$.
    """
    d = 8
    Z, X = clock(2), shift(2)
    indices = list(product([0,1], repeat=6))
    D = np.array([kron(np.linalg.matrix_power(X, I[0]) @ np.linalg.matrix_power(Z, I[1]),\
                       np.linalg.matrix_power(X, I[2]) @ np.linalg.matrix_power(Z, I[3]),\
                       np.linalg.matrix_power(X, I[4]) @ np.linalg.matrix_power(Z, I[5])) for I in indices])
    return frame_povm((D @ hoggar_sic_fiducial()).T.reshape(d, d**2)/np.sqrt(d))