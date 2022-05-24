import numpy as np


class Atoms:
    '''Atoms object that holds all system and cell parameters.'''
    def __init__(self, atom, X, a, ecut, Z, s, f, Ns):
        self.atom = atom
        self.X = X
        self.a = a
        self.ecut = ecut
        self.Z = Z
        self.s = s
        self.f = f
        self.Ns = Ns
        self.initialize()

    def initialize(self):
        '''Initialize and build all necessary parameters.'''
        M, N = self._get_index_matrices()
        self._set_cell(M)
        self._set_G(N)

    def _get_index_matrices(self):
        '''
            Build index matrices M and N to build the real and reciprocal space samplings.
            Latex: List 3.4
                   List 3.5
        '''
        ms = np.arange(np.prod(self.s))
        m1 = ms % self.s[0]
        m2 = np.floor(ms / self.s[0]) % self.s[1]
        m3 = np.floor(ms / (self.s[0] * self.s[1])) % self.s[2]
        M = np.column_stack((m1, m2, m3))

        n1 = m1 - (m1 > self.s[0] / 2) * self.s[0]
        n2 = m2 - (m2 > self.s[1] / 2) * self.s[1]
        n3 = m3 - (m3 > self.s[2] / 2) * self.s[2]
        N = np.column_stack((n1, n2, n3))
        return M, N

    def _set_cell(self, M):
        '''
            Build the unit cell and create the respective sampling.
            Latex: Eq. 3.3
                   List. 3.3
                   Eq. 3.5
                   List. 3.3
        '''
        R = self.a * np.eye(3)
        self.R = R
        self.Omega = np.abs(np.linalg.det(R))
        self.r = M @ np.linalg.inv(np.diag(self.s)) @ R.T
        return

    def _set_G(self, N):
        '''
            Build G-vectors, build squared magnitudes G2, and generate the active space.
            Latex: Eq. 3.8
                   List. 3.5
                   List. 3.6
                   List. 3.7
                   Eq. 3.9
                   List. 3.8
        '''
        G = 2 * np.pi * N @ np.linalg.inv(self.R)
        self.G = G
        G2 = np.sum(G**2, axis=1)
        self.G2 = G2
        active = np.nonzero(G2 <= 2 * self.ecut)
        self.active = active
        self.G2c = G2[active]
        self.Sf = np.sum(np.exp(-1j * self.G @ self.X.conj().T), axis=1)
        return
