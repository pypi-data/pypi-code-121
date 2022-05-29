import numpy as np
import scipy as sc
from functools import reduce

def state_space_dimension(d, field):
    r"""
    Returns the dimension of the state space for a give pure state space dimension and number field.
    """
    if field == "complex":
        n = int(d**2)
    elif field == "real":
        n = int(d*(d+1)/2)
    return n

def normalize(v):
    r"""
    Normalizes vector.
    """
    return v/np.linalg.norm(v)

def spectral_inverse(M):
    r"""
    Spectral/group inverse.
    """
    U, D, V = np.linalg.svd(M)
    m = (np.isclose(D, 0)).argmax()
    m = m if m != 0 else M.shape[0]
    B = U[:, :m]
    C = np.diag(D[:m]) @ V[:m, :]
    return (B @ np.linalg.matrix_power(C @ B, -2) @ C)

def basis(d, i):
    r"""
    Returns basis vectors.
    """
    return np.eye(d)[i]

def paulis():
    r"""
    Returns Pauli matrices.
    """
    X = np.array([[0, 1], [1, 0]])
    Y = np.array([[0, -1j], [1j, 0]])
    Z = np.array([[1, 0], [0, -1]])
    return np.array([np.eye(2), X, Y, Z])

def kron(*args):
    r"""
    Numpy's kronecker product with a variable number of arguments.
    """
    return reduce(lambda x, y: np.kron(x, y), args)

def vn_povm(H):
    r"""
    Returns a P(O)VM corresponding to the eigenstates of a Hermitian operator.
    """
    return np.array([np.outer(v, v.conj().T) for v in np.linalg.eig(H)[1][::-1]])

def discriminator_povm(a, b):
    r"""
    Returns a non informationally complete POVM which has the special property
    of distinguishing between two arbitrary states $\mid a \rangle$ and $\mid b\rangle$, which are not necessarily orthogonal (which is impossible with a standard PVM).

    It has three elements:

    $$ \hat{F}_{a} = \frac{1}{1+\mid\langle a \mid b \rangle\mid}(\hat{I} - \mid b \rangle \langle b \mid) $$
    $$ \hat{F}_{b} = \frac{1}{1+\mid\langle a \mid b \rangle\mid}(\hat{I} - \mid a \rangle \langle a \mid) $$
    $$ \hat{F}_{?} = \hat{I} - \hat{F}_{a} - \hat{F}_{b} $$

    The first tests for "not B", the second tests for "not A", and the third outcome represents an inconclusive result.
    """
    d = a.shape[0]
    p = abs(a.conj().T @ b)
    Fa = (1/(1+p))*(np.eye(d) - b @ b.conj().T)
    Fb = (1/(1+p))*(np.eye(d) - a @ b.conj().T)
    Fq = np.eye(d) - Fa - Fb
    return np.array([Fa, Fb, Fq])

def partial_trace_kraus(keep, dims):
    r"""
    Constructs the Kraus map corresponding to the partial trace. Takes `keep` which is a single index or list of indices denoting
    subsystems to keep, and a list `dims` of dimensions of the overall tensor product Hilbert space. 

    For illustration, to trace over the $i^{th}$ subsystem of $n$, one would construct Kraus operators:

    $$ \hat{K}_{i} = I^{\otimes i - 1} \otimes \langle i \mid \otimes I^{\otimes n - i}$$.
    """
    if type(keep) == int:
        keep = [keep]
    trace_over = [i for i in range(len(dims)) if i not in keep]
    indices = [{trace_over[0]:t} for t in range(dims[trace_over[0]])]
    for i in trace_over[1:]:
        new_indices = []
        for t in range(dims[i]):
            new_indices.extend([{**j, **{i: t}} for j in indices])
        indices = new_indices
    return np.array([kron(*[np.eye(d) if i in keep else basis(d, index[i]) for i, d in enumerate(dims)]) for index in indices])

def tighten_frame(R):
    r"""
    Tightens frame.
    """
    return sc.linalg.polar(R)[0]

def frame_povm(R):
    r"""
    Lifts tight frame to POVM.
    """
    return np.array([np.outer(r, r.conj()) for r in R.T])

def fft_matrix(d):
    r"""
    Finite fourier transform matrix.
    """
    w = np.exp(-2*np.pi*1j/d)
    return np.array([[w**(i*j) for j in range(d)] for i in range(d)])/np.sqrt(d)

def gellman_basis(d):
    r"""
    Hermitian operator basis.
    """
    def h_helper(d,k):
        if k == 1:
            return np.eye(d)
        if k > 1 and k < d:
            return sc.linalg.block_diag(h_helper(d-1, k), [0])
        if k == d:
            return np.sqrt(2/(d*(d+1)))*sc.linalg.block_diag(np.eye(d-1), [1-d])

    E = [[np.zeros((d,d)) for k in range(d)] for j in range(d)]
    for j in range(d):
        for k in range(d):
            E[j][k][j,k] = 1
    F = []
    for j in range(d):
        for k in range(d):
            if k < j:
                F.append(E[k][j] + E[j][k])
            elif k > j:
                F.append(-1j*(E[j][k] - E[k][j]))
    F.extend([h_helper(d, k) for k in range(1,d+1)])
    return np.array([f/np.sqrt((f@f).trace()) for f in F])

def upgrade(O, i, dims):
    return kron(*[O if i == j else np.eye(d) for j, d in enumerate(dims)])

def squish_povm(E):
    S = sc.linalg.fractional_matrix_power(sum(E), -1/2)
    return np.array([S @ e @ S for e in E])

def implement_povm(E):
    n, d = len(E), E[0].shape[0]
    aux_projectors = [kron(np.eye(d), np.outer(basis(n,i), basis(n,i))) for i in range(n)]
    V = sum([kron(sc.linalg.sqrtm(E[i]), basis(n, i)) for i in range(n)])
    Q, R = np.linalg.qr(V, mode="complete")
    for i in range(d):
        Q.T[[i,n*i]] = Q.T[[n*i,i]]
        Q[:,n*i] = V[:,i].T
    return Q

def complete_povm(E):
    return np.array(E/len(E) + [np.eye(E[0].shape[0]) - sum(E)/len(E)])
