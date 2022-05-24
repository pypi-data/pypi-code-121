import numpy as np


def diagprod(a, B):
    '''Efficiently calculate the expression Diag(a) * B.'''
    a_col = a[:, None]
    return a_col * B


def sqrtm(A):
    '''Calculate the matrix square root of A.'''
    evals, evecs = np.linalg.eig(A)
    return evecs @ np.diag(np.sqrt(evals)) @ np.linalg.inv(evecs)
