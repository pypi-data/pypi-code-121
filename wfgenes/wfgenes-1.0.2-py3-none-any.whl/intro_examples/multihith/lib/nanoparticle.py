""" building and manipulating nanoparticle models """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2018, Karlsruhe Institute of Technology'

import numpy as np
from ase import Atom
from ase import Atoms
from ase.neighborlist import NeighborList
from ase.constraints import FixAtoms
from igraph import Graph
from uuid import uuid4
from atomsutils import make_graph
from substrate import Substrate
from substrate import SubstrateAdsorbateComplex

class Nanoparticle(Substrate):
    """ a general nanoparticle class currently restricted to fcc crystalline
        nanoparticles
        TODO: Nanoparticle(Substrate) """
    types = [
        'free atom',
        'ontop adatom',
        'bridge adatom',
        'hollow adatom',
        '111 vertex',
        'surface',
        '100-110 edge, 111-111-100 vertex',
        '110 surface (top), 111-111 edge, 110-111 edge',
        '100 surface',
        '111 surface',
        'unknown',
        '110 surface (bottom)',
        'bulk'
    ]
    site_cns = {
        '4-fold hollow': [
            (5, 5, 5, 5), (6, 6, 6, 6), (5, 7, 7, 8), (6, 7, 7, 8),
            (7, 7, 8, 8), (8, 8, 8, 8)
        ],
        '3-fold hollow': [
            (5, 5, 5), (7, 7, 7), (4, 7, 7), (7, 7, 9), (7, 9, 9), (9, 9, 9),
            (6, 6, 9), (5, 7, 7), (6, 7, 9), (6, 6, 10), (6, 6, 11),
            (6, 7, 10), (6, 7, 11), (7, 9, 10), (7, 9, 11), (7, 10, 10),
            (7, 10, 11), (7, 11, 11), (9, 9, 10), (9, 10, 10), (9, 9, 11),
            (9, 10, 11), (9, 11, 11)
        ]
    }
    top_site_max_coord = 10
    neighborlist = []
    coordination = []
    atomtype = []
    ads_sites = []

    def __init__(self, atoms, cutoff=1.4):
        assert not any(atoms.pbc), 'periodic system detected'
        self.cutoff = cutoff
        self.atoms = atoms
        self.build_neighborslists()
        self.build_adsorption_sites()

    def copy(self):
        from copy import deepcopy
        new_np = self.__class__(self.atoms, cutoff=self.cutoff)
        new_np.atoms = self.atoms.copy()
        new_np.graph = self.graph.copy()
        new_np.atomtype = deepcopy(self.atomtype)
        new_np.ads_sites = deepcopy(self.ads_sites)
        new_np.coordination = deepcopy(self.coordination)
        new_np.neighborlist = deepcopy(self.neighborlist)
        return new_np

    def build_neighborslists(self):
        """ build a neighborlist, graph, asign coordination numbers """
        self.neighborlist = []
        self.coordination = []
        self.atomtype = []
        nl = NeighborList(
            cutoffs=len(self.atoms)*[self.cutoff],
            bothways=True,
            self_interaction=False
        )
        nl.update(self.atoms)
        for atom in self.atoms:
            neighb = nl.get_neighbors(atom.index)[0]
            coord = len(neighb)
            self.neighborlist.append(neighb.tolist())
            self.coordination.append(coord)
            self.atomtype.append(self.types[coord])
        self.graph = make_graph(self.atoms)

    def build_adsorption_sites(self):
        """ constructs all kinds of adsorption sites """
        self.ads_sites = []
        g = Graph(len(self.atoms))
        nl = NeighborList(
            cutoffs=len(self.atoms)*[self.cutoff],
            bothways=False,
            self_interaction=False
        )
        nl.update(self.atoms)
        neighborlist = [nl.get_neighbors(atom.index)[0].tolist()
                        for atom in self.atoms]
        for index, surfatom in enumerate(neighborlist):
            if self.atomtype[index] != 'bulk':
                for neighbor in surfatom:
                    if self.atomtype[neighbor] != 'bulk':
                        g.add_edge(index, neighbor)

        bulkatoms = [a.position for a in self.atoms
                     if self.atomtype[a.index] == 'bulk']
        self.bulkref = np.sum(bulkatoms, axis=0)/len(bulkatoms)

        self.build_on_top_sites(g)
        self.build_bridge_sites(g)

        for clen, kind in zip([3, 4], ['3-fold hollow', '4-fold hollow']):
            self.build_cyclic_sites(g, clen, kind)

        self.set_site_types()
        self.set_site_cns()
        self.set_site_gcns()

    def build_on_top_sites(self, g):
        for vertex in g.vs.indices:
            if self.coordination[vertex] < self.top_site_max_coord:
                # only neighbors from the surface
                neighbors = [self.atoms[ind] for ind in g.neighbors(vertex)]
                self.ads_sites.append(
                    AdsorptionSite([self.atoms[vertex]], 'on-top',
                                   bulkref=self.bulkref, neighbors=neighbors))

    def get_bridge_common_neighbors(self, g, vertex1, vertex2):
        """ find axial common neighbors of vertex1 and vertex2 """
        neighborset = {n for n in g.neighbors(vertex1) if n != vertex2}
        neighborset.intersection_update(
            {n for n in g.neighbors(vertex2) if n != vertex1})
        if len(neighborset) < 2:
            # the case of a bridge site on 100, 010 or 001 surfaces
            # any atoms that are common neighbors of vertex1 and vertex2
            neighborset = set(self.neighborlist[vertex1])
            neighborset.intersection_update(
                {n for n in self.neighborlist[vertex2] if n != vertex1})
        assert len(neighborset) > 0
        neighbors = [self.atoms[ind] for ind in neighborset]
        return neighbors

    def build_bridge_sites(self, g):
        for edge in g.es:
            (vertex1, vertex2) = edge.tuple
            neighbors = self.get_bridge_common_neighbors(g, vertex1, vertex2)
            if len(neighbors) < 3:
                atoms = [self.atoms[vertex1], self.atoms[vertex2]]
                self.ads_sites.append(
                    AdsorptionSite(atoms, 'bridge',
                                   bulkref=self.bulkref, neighbors=neighbors))

    def build_cyclic_sites(self, g, clen, kind):
        lst = [sorted(l) for l in g.get_subisomorphisms_vf2(Graph.Ring(clen))]
        sites = [list(x) for x in set(tuple(x) for x in lst)]
        for site in sites:
            atoms = [self.atoms[idx] for idx in site]
            cns = tuple(sorted([self.coordination[idx] for idx in site]))
            if any(cns == cn for cn in self.site_cns[kind]):
                self.ads_sites.append(
                    AdsorptionSite(atoms, kind, bulkref=self.bulkref,
                                   neighbors=self.get_site_neighbors(site)))

    def get_site_neighbors(self, site):
        neighborset = {n for idx in site for n in self.neighborlist[idx]}
        return [self.atoms[ind] for ind in neighborset]

    def set_constraints(self, level='all'):
        """ Sets FixAtoms constraints in the nanoparticle.
        Possible values for the 'level' argument are:
        - 'all': all atoms fixed (default)
        - 'none': no atoms fixed
        - 'bulk': all bulk atoms fixed
        - 1, 2, 3, ...: only these first layers are relaxed
        - 'sites': only atoms of occupied sites are relaxed
        - 'neighbors': only atoms and neighbors of occupied sites are relaxed
        """
        layers = None
        string_args = ['all', 'none', 'bulk', 'sites', 'neighbors']
        assert (isinstance(level, int) and level > 0) or level in string_args
        if level == 'all':
            self.atoms.set_constraint(FixAtoms(mask=len(self.atoms)*[True]))

        if level == 'bulk':
            layers = 1

        if isinstance(level, int):
            layers = level

        if layers is not None:
            g = self.graph.copy()
            # g.vs['id'] = range(len(g.vs))
            for _ in range(layers-1):
                surfs = [s.index for s in g.vs if g.degree(s.index) != 12]
                g.delete_vertices(surfs)
            bulks = [s['id'] for s in g.vs if g.degree(s.index) == 12]
            self.atoms.set_constraint(FixAtoms(indices=bulks))

        if level in ['sites', 'neighbors']:
            mask = len(self.atoms)*[True]            
            for site in self.ads_sites:
                if not site.vacant:
                    for atom in site.atoms:
                        mask[atom.index] = False
            if level == 'neighbors':
                for site in self.ads_sites:
                    if not site.vacant:
                        site_indices = [atom.index for atom in site.atoms]
                        for atom in self.get_site_neighbors(site_indices):
                            mask[atom.index] = False
            self.atoms.set_constraint(FixAtoms(mask=mask))

    def set_site_types(self):
        """ determine the type of adsorption sites for the given kinds """
        for site in self.ads_sites:
            if site.kind == '3-fold hollow':
                ngrs = [set(self.neighborlist[a.index]) for a in site.atoms]
                if len(ngrs[0] & ngrs[1] & ngrs[2]) == 1:
                    site.set_type('hcp')
                else:
                    site.set_type('fcc')
            else:
                site.set_type(None)

    def set_site_cns(self):
        """ determine and set the coordination numbers of site atoms """
        for site in self.ads_sites:
            idxs = [a.index for a in site.atoms]
            cns = tuple(sorted([self.coordination[idx] for idx in idxs]))
            site.set_coordination_numbers(cns)

    def set_site_gcns(self):
        """ set the generalized coordination numbers for all sites """
        for site in self.ads_sites:
            sidxs = [a.index for a in site.atoms]
            gcn = self.get_gcn(sidxs)
            site.set_gcn(gcn)

    def modify_atom(self, mod):
        pass


class AdsorptionSite:
    """ a class to represent an adsorption site """
    kinds = ['on-top', 'bridge', '3-fold hollow', '4-fold hollow']
    types = ['on-top 111', 'on-top 110', 'on-top 100', 'fcc', 'hcp',
             'long bridge', 'short bridge', 'trough', None]
    locations = ['vertex', 'edge', 'facet']
    atoms = None # a list of Atom objects
    neighbors = None # a list of Atom objects
    adsorbate = None # associated adsorbate object
    vacant = True
    surfdir = None
    site_id = None
    cns = None
    gcn = None

    def __init__(self, atoms, kind, neighbors=None, bulkref=None):
        assert kind in self.kinds
        self.atoms = atoms
        self.neighbors = neighbors
        self.kind = kind
        eps = np.sqrt(np.finfo(np.float).eps)

        atoms_positions = [a.position for a in atoms]
        centroid = 1./len(atoms)*np.sum(atoms_positions, axis=0)
        if kind in ['3-fold hollow', '4-fold hollow']:
            m0 = atoms[-1].position - centroid
            for atom in atoms:
                m1 = atom.position - centroid
                normal = np.cross(m0, m1)
                # test colinearity for 4-fold hollow site
                if np.linalg.norm(normal) > eps:
                    break

        if kind in ['bridge', 'on-top']:
            assert len(neighbors) > 0
            neigh_positions = [a.position for a in neighbors]
            ncentroid = 1./len(neighbors)*np.sum(neigh_positions, axis=0)
            normal = centroid - ncentroid
            # coplanar atoms and neighbors
            if np.linalg.norm(normal) < eps:
                ref = atoms[0] if kind == 'bridge' else neighbors[-1]
                m0 = ref.position - centroid
                for neighbor in neighbors:
                    m1 = neighbor.position - centroid
                    normal = np.cross(m0, m1)
                    # test colinearity
                    if np.linalg.norm(normal) > eps:
                        break

        assert(np.linalg.norm(normal) > eps)
        normal = normal/np.linalg.norm(normal)
        self.surfdir = np.dot(centroid - bulkref, normal)
        norm = abs(self.surfdir)
        if norm > eps:
            self.surfdir = self.surfdir / norm
        self.centroid = centroid
        self.normal = normal
        self.site_id = uuid4()

    def get_kind(self):
        return self.kind

    def set_type(self, stype):
        assert stype in self.types
        self.stype = stype

    def get_type(self):
        return self.stype

    def set_location(self, location):
        assert location in self.locations
        self.location = location

    def get_location(self):
        return self.location

    def set_coordination_numbers(self, cns):
        self.cns = cns

    def get_coordination_numbers(self):
        return self.cns

    def set_gcn(self, gcn):
        """ set the generalized coordination number """
        self.gcn = gcn

    def get_gcn(self):
        """ get the generalized coordination number """
        return self.gcn

    def add_adsorbate(self, zmat, alignment):
        assert self.vacant
        self.adsorbate = Adsorbate(self, zmat, alignment)
        self.vacant = False

    def get_atoms(self):
        return Atoms(self.atoms)

    def get_adsorbate(self):
        if not self.vacant:
            return self.adsorbate


class Adsorbate:
    """ a class to represent a mono-dentate adsorbate """
    site = None # associated site object
    graph = None # adsorbate's graph
    atoms = None # Atoms object containing the adsorbate atoms

    def __init__(self, site, zmat, align):
        """ """
        from zmatrix import Atoms
        assert site.vacant
        assert len(zmat) > 0
        assert ((len(zmat) == len(align) == 1) or
                (len(zmat) == 2 and len(align) == 3) or
                (len(zmat) > 2 and len(align) == 4))
        self.site = site
        site.adsorbate = self
        auxa = self._construct_aux_atoms(zmat, align)
        auxz = self._construct_aux_zmat(auxa, zmat, align)
        positions = auxa.get_positions().tolist()
        self.atoms = Atoms.from_zmat(auxz, positions=positions)
        del self.atoms[:2] # delete the auxiliary atoms
        self.graph = make_graph(self.atoms)
        self.site.vacant = False

    def _construct_aux_atoms(self, zmat, align):
        """ construct auxiliary atoms object """
        si = self.site
        a0 = si.neighbors[-1] if si.kind == 'on-top' else si.atoms[-1]
        auxa = Atoms([a0])
        auxa += Atom('X', position=si.centroid)
        a1pos = si.centroid + align[0]*si.normal*si.surfdir
        auxa += Atom(zmat[0]['symbol'].capitalize(), a1pos)
        return auxa

    def _construct_aux_zmat(self, auxa, zmat, align):
        """ construct auxiliary z-matrix """
        auxz = [{'label': 'auxa0', 'symbol': auxa[0].symbol}]
        auxz.append({'label': 'auxa1', 'symbol': 'X',
                     'distance': {
                         'reference': 'auxa0',
                         'value': auxa.get_distance(0, 1)
                    }})
        auxz.extend([line.copy() for line in zmat])
        auxz[2]['distance'] = {'reference': 'auxa1', 'value': align[0]}
        auxz[2]['angle'] = {
            'reference': 'auxa0',
            'value': auxa.get_angle(0, 1, 2)
        }
        if len(zmat) > 1:
            auxz[3]['angle'] = {'reference': 'auxa1', 'value': align[1]}
            auxz[3]['dihedral'] = {'reference': 'auxa0', 'value': align[2]}
        if len(zmat) > 2:
            auxz[4]['dihedral'] = {'reference': 'auxa1', 'value': align[3]}
        return auxz

    def get_atoms(self):
        return self.atoms.copy()


class NanoparticleAdsorbateComplex(SubstrateAdsorbateComplex):
    """ represent a cluster-adsorbate complex """
    def __init__(self, nanoparticle, site_ids, ads_params,
                 cluster_constraints='none', vacuum=None):
        np = nanoparticle.copy()
        self.ads_sites = [s for s in np.ads_sites if s.site_id in site_ids]
        zmats = [ads['zmat'] for ads in ads_params]
        aligns = [ads['alignment'] for ads in ads_params]
        for site, zmat, align in zip(self.ads_sites, zmats, aligns):
            site.add_adsorbate(zmat, align)
        np.set_constraints(level=cluster_constraints)
        adsorbates = [site.adsorbate for site in self.ads_sites]
        self.atoms = np.atoms
        for ads, par in zip(adsorbates, ads_params):
            magmoms = par.get('initial magnetic moments', None)
            ads.atoms.set_initial_magnetic_moments(magmoms)
            self.atoms += ads.atoms
        self.add_vacuum(vacuum)
        self.graph = make_graph(self.atoms)


def get_all_complexes(np, site_ids, ads_params, **kwargs):
    """ generate all possible nanoparticle-adsorbate complexes """
    from itertools import permutations
    return [NanoparticleAdsorbateComplex(np, stuple, ads_params, **kwargs)
            for stuple in permutations(site_ids, len(ads_params))]


def yield_all_complexes(np, site_ids, ads_params, progress=False, **kwargs):
    """ generate all possible nanoparticle-adsorbate complexes """
    from itertools import permutations
    from tqdm import tqdm
    itera = permutations(site_ids, len(ads_params))
    total = len(list(permutations(site_ids, len(ads_params))))
    tqdm_itera = tqdm(itera, total=total, miniters=10) if progress else itera
    for stuple in tqdm_itera:
        yield NanoparticleAdsorbateComplex(np, stuple, ads_params, **kwargs)
