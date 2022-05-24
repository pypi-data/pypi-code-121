import numpy as np

from .dft import orth
from .energies import get_Eewald
from .minimizer import sd
from .operators import PWBasis
from .potentials import coulomb


class SCF:
    '''SCF function to handle direct minimizations.'''
    def __init__(self, atoms):
        self.atoms = atoms
        self.op = PWBasis(atoms)
        self.pot = coulomb(self.atoms, self.op)
        self._init_W()

    def run(self, Nit=1001, beta=1e-5, etol=1e-6):
        '''Run the self-consistent field (SCF) calculation.'''
        self.Eewald = get_Eewald(self.atoms)
        self.Etot = sd(self, Nit, beta, etol)
        return self.Etot

    def _init_W(self, seed=1234):
        '''
            Generate random initial-guess coefficients as starting values.
            Latex: List. 3.18
        '''
        np.random.seed(seed)
        W = np.random.randn(len(self.atoms.G2c), self.atoms.Ns)
        self.W = orth(self.atoms, self.op, W)
        return
