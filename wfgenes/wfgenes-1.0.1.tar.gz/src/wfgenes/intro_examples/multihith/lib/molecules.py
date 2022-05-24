""" Methods to construct, manipulate and analyse molecule objects """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2016, Karlsruhe Institute of Technology'

import math
import numpy as np
from ase.geometry import find_mic


class Molecules:

    _positions = None
    _masses = None
    _cell = None
    _pbc = None

    def __init__(self, **kwargs):
        if 'positions' in list(kwargs.keys()):
            self._positions = np.array(kwargs['positions'])
            self._cell = kwargs['cell']
            self._pbc = kwargs['pbc']
        if 'masses' in list(kwargs.keys()):
            self._masses = np.array(kwargs['masses'])

    @classmethod
    def from_molecules(cls, molecules):
        positions = [mol.get_center_of_mass() for mol in molecules]
        masses = [np.sum(mol.get_masses()) for mol in molecules]
        cell = molecules[0].get_cell()
        pbc = molecules[0].get_pbc()
        return cls(
            positions=positions,
            masses=masses,
            cell=cell,
            pbc=pbc
        )

    @classmethod
    def from_atoms(cls, atoms):
        return cls(
            positions=atoms.get_positions(),
            cell=atoms.get_cell(),
            pbc=atoms.get_pbc()
        )

    @classmethod
    def SimpleCubic(cls, a, size, pbc=True):
        from ase.lattice.cubic import SimpleCubic
        atoms = SimpleCubic(size=size, symbol='X', pbc=pbc, latticeconstant=a)
        return cls.from_atoms(atoms)

    @classmethod
    def FaceCenteredCubic(cls, a, size, pbc=True):
        from ase.lattice.cubic import FaceCenteredCubic
        atoms = FaceCenteredCubic(size=size, symbol='X', pbc=pbc, latticeconstant=a)
        return cls.from_atoms(atoms)

    def __len__(self):
        return len(self._positions)

    def __delitem__(self, index):
        del(self._positions[index])

    def _get_positions(self):
        return self._positions

    def get_positions(self):
        return self._positions.copy()

    def get_masses(self):
        if self._masses is not None:
            return self._masses.copy()

    def get_distance(self, a0, a1, mic=False, vector=False):
        """Return distance between two molecules with indices a0 and a1.

        Use mic=True to use the Minimum Image Convention.
        vector=True gives the distance vector (from a0 to a1).
        """

        R = np.array(self._get_positions())
        D = np.array([R[a1] - R[a0]])
        if mic:
            D, D_len = find_mic(D, self._cell, self._pbc)
        else:
            D_len = np.array([np.sqrt((D**2).sum())])
        if vector:
            return D[0]

        return D_len[0]

    def get_distances(self, a, indices, mic=False, vector=False):
        """Return distances of molecule with index a with a list of molecules.

        Use mic=True to use the Minimum Image Convention.
        vector=True gives the distance vector (from a to self[indices]).
        """

        R = np.array(self._get_positions())
        D = R[indices] - R[a]
        if mic:
            D, D_len = find_mic(D, self._cell, self._pbc)
        else:
            D_len = np.sqrt((D**2).sum(1))
        if vector:
            return D
        return D_len

    def get_all_distances(self, mic=False):
        """Return distances of all of the molecules with all of the molecules.

        Use mic=True to use the Minimum Image Convention.
        """
        L = len(self)
        R = np.array(self._get_positions())

        D = []
        for i in range(L - 1):
            D.append(R[i + 1:] - R[i])
        D = np.concatenate(D)

        if mic:
            D, D_len = find_mic(D, self._cell, self._pbc)
        else:
            D_len = np.sqrt((D**2).sum(1))

        results = np.zeros((L, L), dtype=float)
        start = 0
        for i in range(L - 1):
            results[i, i + 1:] = D_len[start:start + L - i - 1]
            start += L - i - 1
        return results + results.T

    def get_volume(self):
        """Get volume of unit cell."""
        return abs(np.linalg.det(self._cell))

    def get_pbc(self):
        return self._pbc.copy()

    def get_cell(self):
        return self._cell.copy()

    def trim(self, cutoff, directions=(False, False, True)):
        """ cut away border layers of the morphology """
        deletions = []
        for direction, select in enumerate(directions):
            if select:
                minpos = np.amin(np.array(self._positions)[:,direction])
                maxpos = np.amax(np.array(self._positions)[:,direction])
                for index, position in enumerate(self._positions):
                    in_lower = position[direction] < minpos+cutoff
                    in_upper = position[direction] > maxpos-cutoff
                    if in_lower or in_upper:
                        deletions.append(index)
        deletions = list(set(deletions))
        for index in sorted(deletions, reverse=True):
            del(self._positions[index])

    def get_mass(self):
        if self._masses is not None:
            return np.sum(self._masses)

    def get_rdf_ase(self, rmax, nbins, distance_matrix=None):
        ''' Adapted this function from ase.ga.utilities to use mic=True '''
        dm = distance_matrix 
        if dm is None: 
            dm = self.get_all_distances(mic=True)
        rdf = np.zeros(nbins + 1) 
        dr = float(rmax / nbins) 
        for i in range(len(self)): 
            for j in range(i + 1, len(self)): 
                rij = dm[i][j] 
                index = int(math.ceil(rij / dr)) 
                if index <= nbins: 
                    rdf[index] += 1 

        # Normalize 
        phi = len(self) / self.get_volume() 
        norm = 2.0 * math.pi * dr * phi * len(self) 

        dists = [0] 
        for i in range(1, nbins + 1): 
            rrr = (i - 0.5) * dr 
            dists.append(rrr) 
            rdf[i] /= (norm * ((rrr**2) + (dr**2) / 12.)) 

        return rdf, np.array(dists)


    def get_rdf(self, rmax, nbins):
        """ This function works for max 15000 particles """
        bins = np.linspace(0, rmax, nbins)
        distances = self.get_all_distances(mic=True)
        pairs=[]
        for cut, row in enumerate(distances[0:-1]):
            pairs += row.tolist()[cut+1:]
        rdf, edges = np.histogram(pairs, bins=bins, normed=False)
        # centralize the mesh
        r = 0.5 * (edges[1:] + edges[:-1])
        # volumes of the spherical shells betw. r and r+dr for each bin
        volumes = (4. / 3.) * np.pi * (np.power(edges[1:], 3) - np.power(edges[:-1], 3))
        # normalize by the number density
        ndens = len(pairs) / self.get_volume()
        rdf = rdf.astype(np.float) / (ndens * volumes)
        return np.insert(rdf, 0, 0.), np.insert(r, 0, 0.)


    def todict(self):
        """ Returns a morphology dictionary """
        morphology = {}
        morphology['positions'] = self.get_positions().tolist()
        morphology['masses'] = self.get_masses().tolist()
        morphology['pbc'] = self.get_pbc().tolist()
        morphology['cell'] = self.get_cell().tolist()
        return morphology


Morphology = Molecules

