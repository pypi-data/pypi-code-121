import numpy as np

from .utils import diagprod, sqrtm


def solve_poisson(atoms, op, n):
    '''
        Solve the Poisson equation.
        Latex: Eq. 2.48
    '''
    return -4 * np.pi * op.Linv(op.O(op.J(n)))


def get_n_total(atoms, op, Y):
    '''
        Calculate the total electronic density.
        Latex: Eq. 2.36
               List. 3.23
    '''
    Yrs = op.I(Y)
    n = atoms.f * np.real(Yrs.conj() * Yrs)
    return np.sum(n, axis=1)


def orth(atoms, op, W):
    '''
        Orthogonalize coefficient matrix W.
        Latex: Eq. 2.34 ff.
    '''
    U = sqrtm(W.conj().T @ op.O(W))
    return W @ np.linalg.inv(U)


def get_grad(atoms, op, W, Y, n, phi, vxc, Vreciproc):
    '''
        Calculate the energy gradient with respect to W.
        Latex: Eq. 2.43
               List. 3.24
    '''
    F = np.diag(atoms.f)
    HW = H(atoms, op, W, Y, n, phi, vxc, Vreciproc)
    WHW = W.conj().T @ HW
    U = W.conj().T @ op.O(W)
    invU = np.linalg.inv(U)
    U12 = sqrtm(invU)
    Ht = U12 @ WHW @ U12
    return (HW - (op.O(W) @ invU) @ WHW) @ (U12 @ F @ U12) + op.O(W) @ (U12 @ Q(Ht @ F - F @ Ht, U))


def H(atoms, op, W, Y, n, phi, vxc, Vreciproc):
    '''
        Left-hand side of the eigenvalue equation.
        Latex: Eq. 2.45 ff.
               List. 3.26
    '''
    Veff = Vreciproc + op.Jdag(op.O(op.J(vxc) + phi))
    return -0.5 * op.L(W) + op.Idag(diagprod(Veff, op.I(W)))


def Q(inp, U):
    '''
        Operator needed to calculate gradients with non-constant occupations.
        Latex: Eq. 2.47
               List. 3.25
    '''
    mu, V = np.linalg.eig(U)
    mu = mu[:, None]
    denom = np.sqrt(mu) @ np.ones((1, len(mu)))
    denom = denom + denom.conj().T
    return V @ ((V.conj().T @ inp @ V) / denom) @ V.conj().T
