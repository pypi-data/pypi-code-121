""" generic classes and functions for atomic structures """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2018, Karlsruhe Institute of Technology'

from ase import Atoms
from ase.io import read
from morphology import rmsd
from construct import create_structure

class Structure:
    """ generic atomic structure class """

    def __init__(self, **kwargs):
        from atomsutils import make_graph
        from data import Atoms
        atoms = kwargs.get('atoms')
        graph = kwargs.get('graph')
        self.kwargs = kwargs
        self.atoms = None
        self.graph = None
        if atoms:
            self.atoms = atoms.copy() if isinstance(atoms, Atoms) else Atoms.from_dict(atoms)
        elif 'construct' in kwargs:
            self.atoms = create_structure(**kwargs['construct'])
        elif 'input file' in kwargs:
            self.atoms = read(kwargs['input file'])
        else:
            return
        self.add_vacuum(kwargs.get('vacuum'))
        self.graph = graph.copy() if graph else make_graph(self.atoms)
        self.set_tags()
        self.add_modifications(kwargs.get('modifications'))
        self.set_constraints(kwargs.get('constraints'))
        self.set_magnetic_moments(kwargs.get('initial magnetic moments'))

    def copy(self):
        """ create and return a copy of itself """
        kwargs = self.kwargs.copy()
        kwargs['atoms'] = self.atoms
        kwargs['graph'] = self.graph
        return self.__class__(**kwargs)

    def add_modifications(self, mods):
        """ modifications are substitutions of specified individual atoms """
        if mods:
            for mod in mods:
                self.modify_atom(mod)

    def modify_atom(self, mod):
        """ substitute an atom in the structure with another atom """
        pass

    def add_vacuum(self, vacuum):
        """ add vacuum along non-periodic dimensions of the structure """
        if vacuum:
            axis = [i for i, x in enumerate(self.atoms.pbc) if not x]
            self.atoms.center(vacuum=vacuum, axis=axis)

    def set_tags(self):
        """ stub method - tags are used only by subclass methods """
        pass

    def set_constraints(self, constraints):
        """ set generic constraints: input as dicts of constraint objects """
        from ase.constraints import dict2constraint
        if constraints is not None:
            for constr in constraints:
                self.atoms.set_constraint(dict2constraint(constr))

    def set_magnetic_moments(self, magmoms):
        """ initialize atomic magnetic moments """
        if isinstance(magmoms, list):
            self.atoms.set_initial_magnetic_moments(magmoms)
        elif magmoms is not None:
            self.atoms.set_initial_magnetic_moments(len(self.atoms)*[magmoms])

    def get_atoms(self):
        """ return a copy of the atoms object """
        return self.atoms.copy()

    def get_enantiomer(self):
        """ return the enantiomer of the structure using the formula from
            https://en.wikipedia.org/wiki/Transformation_matrix#Reflection_2
        """
        import numpy as np
        from copy import deepcopy
        normal = (1., 1., 1.) # arbitrary mirror plane containing the origin
        normal = normal/np.linalg.norm(normal)
        amat = np.identity(3, dtype=float)-2*np.outer(normal, normal)
        new_obj = deepcopy(self)
        new_obj.atoms.set_positions(np.dot(self.atoms.positions, amat))
        return new_obj

    def get_canonical(self):
        """ return atoms ordered in the canonical permutation of the graph """
        mapping = self.graph.canonical_permutation()
        atoms = Atoms()
        for pos in range(len(mapping)):
            [index] = [i for i, x in enumerate(mapping) if x == pos]
            atoms += self.atoms[index]
        return atoms

    def isomorphic(self, other):
        """ determine if the structure graph is isomorphic to another one """
        if self.is_isomer(other):
            isomorphic = self.graph.isomorphic_vf2(
                other=other.graph,
                color1=self.atoms.get_atomic_numbers(),
                color2=other.atoms.get_atomic_numbers(),
                return_mapping_12=False,
                return_mapping_21=False
            )
        else:
            isomorphic = False
        return isomorphic

    def get_isomorphic_mappings(self, other):
        """ return all isomorphic mapping of the structure graph """
        return self.graph.get_isomorphisms_vf2(
            other=other.graph,
            color1=self.atoms.get_atomic_numbers(),
            color2=other.atoms.get_atomic_numbers()
        )

    def get_isomorphic_structures(self, other):
        """ atoms objects ordered as the isomorphic mappings to other structure """
        structs = []
        for mapping in self.get_isomorphic_mappings(other):
            atoms = Atoms()
            for index in mapping:
                atoms += self.atoms[index]
            structs.append(atoms)
        return structs

    def is_same(self, other, eps=1.e-12):
        """ check whether structure is in agreement with another structure """
        if self.isomorphic(other):
            isomorphic = self.get_isomorphic_structures(other)
            same = any([rmsd(other.atoms, iso) < eps for iso in isomorphic])
        else:
            same = False
        return same

    def is_isomer(self, other):
        """ test if the structure is an isomer of an other structure """
        if len(self.atoms) != len(other.atoms):
            return False
        anum_self = sorted(self.atoms.get_atomic_numbers())
        anum_other = sorted(other.atoms.get_atomic_numbers())
        if any(s != o for s, o in zip(anum_self, anum_other)):
            return False
        return True

    def diff(self, other, enantiomer_test=False):
        """ rmsd of this from another structure """
        assert isinstance(other, self.__class__)
        assert self.is_isomer(other)
        ref = other.get_enantiomer() if enantiomer_test else other
        if self.isomorphic(ref):
            isomorphic = self.get_isomorphic_structures(ref)
            rms = min([rmsd(ref.atoms, iso) for iso in isomorphic])
        else:
            rms = rmsd(ref.atoms, self.atoms)
        return rms


def remove_enantiomers(struct_list):
    """ remove enantiomers from a list of structures """
    new_list = []
    for test in struct_list:
        if not any(test.is_same(c.get_enantiomer()) for c in new_list):
             new_list.append(test)
    return new_list


def get_unique_structures(struct_list):
    """ filter out duplicated structures and return the unique ones """
    uniq = []
    for test in struct_list:
        if not any(test.is_same(c) for c in uniq):
            uniq.append(test)
    return uniq
