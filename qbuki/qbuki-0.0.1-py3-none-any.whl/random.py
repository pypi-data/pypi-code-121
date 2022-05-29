import numpy as np
import scipy as sc
import scipy.linalg
from scipy.stats import ortho_group
from scipy.stats import unitary_group

from .utils import *

def rand_probs(n, m):
    r"""m random probability vectors of length n."""
    return np.random.dirichlet((1,)*n, size=m).T

def rand_ginibre(shape, field="complex"):
    r"""
    Random sample from Ginibre ensemble.
    """
    if field == "complex":
        return np.random.randn(*shape) + 1j*np.random.randn(*shape)
    elif field == "real":
        return np.random.randn(*shape)

def rand_ket(d, field="complex"):
    r"""
    Random ket.
    """
    return normalize(rand_ginibre((d, 1), field=field))

def rand_herm(d, field="complex"):
    r"""
    Random Hermitian (symmetric) matrix.
    """
    X = rand_ginibre((d, d), field=field)
    return (X + X.conj().T)/2

def rand_dm(d, r=None, field="complex"):
    r"""
    Random density matrix.
    """
    r = r if type(r) != type(None) else d
    X = rand_ginibre((d, r), field=field)
    rho = X @ X.conj().T
    return rho/rho.trace()

def rand_unitary(d, field="complex"):
    """
    Random unitary (orthogonal) matrix.
    """
    if field == "complex":
        return unitary_group.rvs(d)
    elif field == "real":
        return ortho_group.rvs(d)

def rand_povm(d, n=None, r=1, field="complex"):
    r"""
    Generates a Haar distributed random POVM for a Hilbert space of dimension $d$, 
    with $n$ elements, and with rank $m$.

    $m$ must satisfy $d \leq mn$, and defaults to $m=1$, giving rank-1 POVM elements.

    $n$ defaults to $d^2$ if complex, $\frac{d(d+1)}{2}$ if real.
    """
    n = n if type(n) != type(None) else state_space_dimension(d, field)

    if field == "complex":
        povm = np.zeros((n, d, d), dtype=np.complex128) 
        S = np.zeros(d, dtype=np.complex128) 
    elif field == "real":
        povm = np.zeros((n, d, d))
        S = np.zeros(d)

    for i in range(n):
        Xi = rand_ginibre((d, r), field=field)
        Wi = Xi @ Xi.conjugate().T
        povm[i, :, :] = Wi
        S = S + Wi
    S = sc.linalg.fractional_matrix_power(S, -1/2)
    for i in range(n):
        Wi = np.squeeze(povm[i, :, :])
        povm[i, :, :] = S @ Wi @ S
    return povm

def rand_effect(d, n=None, r=1, field="complex"):
    r"""
    Generates a Haar distributed random POVM effect of Hilbert space dimension $d$, 
    as if it were part of a POVM of $n$ elements with rank $m$. 
    """
    n = n if type(n) != type(None) else state_space_dimension(d, field)

    X = rand_ginibre((d, r), field=field)
    W = X @ X.conjugate().T
    Y = rand_ginibre((d, (n-1)*r), field=field)
    S = W + Y @ Y.conjugate().T
    S = sc.linalg.fractional_matrix_power(S, -1/2)
    return S @ W @ S.conjugate().T

def rand_ftf(d, n=None, field="complex", rtol=1e-15, atol=1e-15):
    """
    Random tight frame.
    """
    n = n if type(n) != type(None) else state_space_dimension(d, field)
    if field == "complex":
        R = np.random.randn(d, n) + 1j*np.random.randn(d, n) 
    elif field == "real":
        R = np.random.randn(d, n)
    return tighten_frame(R)

def rand_funtf(d, n=None, field="complex", rtol=1e-15, atol=1e-15):
    r"""
    Random finite unit norm tight frame.
    """
    n = n if type(n) != type(None) else state_space_dimension(d, field)
    if field == "complex":
        R = np.random.randn(d, n) + 1j*np.random.randn(d, n) 
    elif field == "real":
        R = np.random.randn(d, n)
    done = False
    while not (np.allclose(R @ R.conj().T, (n/d)*np.eye(d), rtol=rtol, atol=atol) and\
               np.allclose(np.linalg.norm(R, axis=0), np.ones(n), rtol=rtol, atol=atol)):
        R = sc.linalg.polar(R)[0]
        R = np.array([state/np.linalg.norm(state) for state in R.T]).T
    return sc.linalg.polar(R)[0]

def rand_kraus_operators(d, n, field="complex"):
    r"""
    Random Kraus operators.
    """
    G = [rand_ginibre((d, d), field=field) for i in range(n)]
    H = sum([g.conj().T @ g for g in G])
    S = sc.linalg.fractional_matrix_power(H, -1/2)
    return np.array([g @ S for g in G])
