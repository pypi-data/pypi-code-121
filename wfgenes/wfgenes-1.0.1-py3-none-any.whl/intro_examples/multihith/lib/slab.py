""" building and manipulating periodic slab models """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2018, Karlsruhe Institute of Technology'

from ase import Atoms
from ase.build import add_adsorbate
from ase.constraints import FixAtoms
from atomsutils import make_graph
from substrate import Substrate, SubstrateAdsorbateComplex

class Slab(Substrate):
    """ periodic slab structure """
    def __init__(self, params):
        super(Slab, self).__init__(**params)
        self.params = params

    def modify_atom(self, modification):
        from surface import modify_surface_atom
        modify_surface_atom(self.atoms, **modification)

    def set_constraints(self, constraints):
        """ slab-specific types of constraints """
        if constraints is None:
            return
        if all('layers' not in c for c in constraints):
            super(Slab, self).set_constraints(constraints)
            return
        for constraint in constraints:
            cmask = [atom.tag in constraint['layers'] for atom in self.atoms]
            self.atoms.set_constraint(FixAtoms(mask=cmask))

    def copy(self):
        """ create and return a copy of itself """
        return self.__class__(self.params)


class SlabAdsorbateComplex(SubstrateAdsorbateComplex):
    """ represent a slab-adsorbate complex """
    def __init__(self, slab, ads_params, constraints=None, vacuum=None):
        from copy import deepcopy
        ads_params_c = deepcopy(ads_params)
        self.atoms = slab.atoms.copy()
        for ads in ads_params_c:
            if isinstance(ads['adsorbate'], dict):
                ads['adsorbate'] = Atoms(**ads['adsorbate'])
            else:
                assert isinstance(ads['adsorbate'], Atoms)
            add_adsorbate(self.atoms, **ads)
        self.add_vacuum(vacuum)
        self.graph = make_graph(self.atoms)
        self.set_constraints(constraints)

    def set_constraints(self, constraints):
        pass


def get_all_complexes(slab, sites, ads_params, **kwargs):
    """ generate all possible slab-adsorbate complexes """
    from itertools import permutations
    complexes = []
    for stuple in permutations(sites, len(ads_params)):
        upd_pars = [{**ads, **site} for site, ads in zip(stuple, ads_params)]
        complexes.append((SlabAdsorbateComplex(slab, upd_pars, **kwargs), upd_pars))
    return complexes


def yield_all_complexes(slab, sites, ads_params, progress=False, **kwargs):
    """ generate all possible slab-adsorbate complexes - generator version """
    from itertools import permutations
    from tqdm import tqdm
    itera = permutations(sites, len(ads_params))
    total = len(list(permutations(sites, len(ads_params))))
    tqdm_itera = tqdm(itera, total=total, miniters=10) if progress else itera
    for stuple in tqdm_itera:
        upd_pars = [{**ads, **site} for site, ads in zip(stuple, ads_params)]
        yield (SlabAdsorbateComplex(slab, upd_pars, **kwargs), upd_pars)


def get_unique_complexes(complexes):
    """ filter out duplicated complexes and return the unique ones """
    unique = []
    for test in complexes:
        if not any(test[0].isomorphic(c[0]) for c in unique):
            unique.append(test)
    return unique
