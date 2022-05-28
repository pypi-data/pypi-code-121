from .settings import adsorbate_elements
from .utilities import (expand_cell, 
                        get_mic, 
                        custom_warning,
                        is_list_or_tuple, 
                        cart_to_frac, 
                        hash_composition, 
                        neighbor_shell_list, 
                        get_adj_matrix)
from .labels import (get_monometallic_cluster_labels, 
                     get_monometallic_slab_labels,
                     get_bimetallic_cluster_labels, 
                     get_bimetallic_slab_labels,
                     get_multimetallic_cluster_labels, 
                     get_multimetallic_slab_labels)
from ase.data import reference_states, atomic_numbers
from ase.constraints import ExpCellFilter
from ase.geometry import find_mic, wrap_positions
from ase.optimize import BFGS, FIRE
from ase import Atoms
from asap3.analysis import rdf, FullCNA 
from asap3 import FullNeighborList
from asap3 import EMT as asapEMT
from scipy.spatial.distance import pdist, squareform
from collections import defaultdict, Counter
from itertools import combinations, groupby
import networkx as nx
import numpy as np
import warnings
import scipy
import math
import re
warnings.formatwarning = custom_warning


class ClusterAdsorptionSites(object):
    """Base class for identifying adsorption sites on a nanoparticle.
    Support common nanoparticle shapes including: Mackay icosahedron, 
    (truncated) octahedron and (Marks) decahedron.

    The information of each site is stored in a dictionary with the 
    following keys:

    **'site'**: the site type, support 'ontop', 'bridge', 'longbridge', 
    'shortbridge', 'fcc', 'hcp', '3fold', '4fold', '5fold', '6fold'.

    **'surface'**: the surface of the site, support 'vertex', 'edge',
    'fcc100', 'fcc111'.

    **'position'**: the 3D Cartesian coordinate of the site saved as a
    numpy array.

    **'normal'**: the surface normal vector of the site saved as a numpy
    array.

    **'indices'**: the indices of the atoms that constitute the site.

    **'composition'**: the elemental composition of the site. Always in 
    the lowest lexicographical order.

    **'subsurf_index'**: the index of the subsurface atom underneath an
    hcp or 4fold site.

    **'subsurf_element'**: the element of the subsurface atom underneath
    an hcp or 4fold site

    **'label'**: the numerical label assigned to the site if label_sites
    is set to True. 

    Parameters
    ----------
    atoms : ase.Atoms object
        The atoms object must be a non-periodic nanoparticle.
        Accept any ase.Atoms object. No need to be built-in.

    allow_6fold : bool, default False
        Whether to allow the adsorption on 6-fold subsurf sites 
        underneath fcc hollow sites.

    composition_effect : bool, default False
        Whether to consider sites with different elemental 
        compositions as different sites. It is recommended to 
        set composition_effect=False for monometallics.

    ignore_bridge_sites : bool, default False
        Whether to ignore bridge sites.

    label_sites : bool, default False
        Whether to assign a numerical label to each site.
        Labels for different sites are listed in acat.labels.
        Use the bimetallic labels if composition_effect=True,
        otherwise use the monometallic labels.

    surrogate_metal : str, default None
        The code is parameterized w.r.t. pure transition metals.
        The generalization of the code is achieved by mapping all 
        input atoms to a surrogate transition metal that is 
        supported by the asap3.EMT calculator (Ni, Cu, Pd, Ag, Pt 
        or Au). Try changing the surrogate metal when the site 
        identification is not satisfying. If no surrogate metal is
        provided, but the majority of the nanoparticle is a metal       
        supported by asap3.EMT, the surrogate metal will be set to 
        that metal automatically.

    tol : float, default 0.5
        The tolerence of neighbor distance (in Angstrom).
        Might be helpful to adjust this if the site identification 
        is not satisfying. When the nanoparticle is small (less
        than 300 atoms), Cu is normally the better choice, while 
        Au should be good for larger nanoparticles.

    Example
    -------
    The following example illustrates the most important use of a
    `ClusterAdsorptionSites` object - getting all adsorption sites:

        >>> from acat.adsorption_sites import ClusterAdsorptionSites
        >>> from ase.cluster import Octahedron
        >>> atoms = Octahedron('Ni', length=7, cutoff=2)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Pt' 
        >>> atoms.center(vacuum=5.)
        >>> cas = ClusterAdsorptionSites(atoms, allow_6fold=False,
        ...                              composition_effect=True,
        ...                              label_sites=True)
        >>> sites = cas.get_sites()
        >>> print(sites[0])

    Output:

    .. code-block:: python

        {'site': 'bridge', 'surface': 'fcc111', 
         'position': array([6.96,  7.94, 11.86]), 
         'normal': array([-0.66666667, -0.66666667, -0.33333333]), 
         'indices': (0, 2), 'composition': 'PtPt', 
         'subsurf_index': None, 'subsurf_element': None, 'label': 14}

    """

    def __init__(self, atoms, 
                 allow_6fold=False, 
                 composition_effect=False, 
                 label_sites=False,
                 ignore_bridge_sites=False,
                 surrogate_metal=None,
                 tol=.5):

        assert True not in atoms.pbc, 'the cell must be non-periodic'
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

        atoms = atoms.copy()
        for dim in range(3):
            if np.linalg.norm(atoms.cell[dim]) == 0:
                atoms.cell[dim][dim] = np.ptp(atoms.positions[:, dim]) + 10.
        del atoms.constraints
        del atoms[[a.index for a in atoms if 'a' not in reference_states[a.number]]]
        del atoms[[a.index for a in atoms if a.symbol in adsorbate_elements]]

        self.atoms = atoms
        self.positions = atoms.positions
        self.symbols = atoms.symbols
        self.numbers = atoms.numbers
        self.indices = list(range(len(self.atoms)))
        self.allow_6fold = allow_6fold
        self.composition_effect = composition_effect
        self.ignore_bridge_sites = ignore_bridge_sites
        self.surrogate_metal = surrogate_metal
        self.tol = tol
        
        self.ref_atoms = self.mapping(atoms)
        self.cell = atoms.cell
        self.pbc = atoms.pbc
        self.metals = sorted(list(set(atoms.symbols)), 
                             key=lambda x: atomic_numbers[x])
        self.label_sites = label_sites

        if self.composition_effect:
            if len(self.metals) <= 2:
                if len(self.metals) == 1:
                    self.metals *= 2                
                self.label_dict = get_bimetallic_cluster_labels(self.metals)
            else:
                self.label_dict = get_multimetallic_cluster_labels(self.metals)
        else: 
            self.label_dict = get_monometallic_cluster_labels()

        self.fullCNA = {}
        self.make_fullCNA()
        self.set_first_neighbor_distance_from_rdf()
        self.site_dict = self.get_site_dict()
        self.make_neighbor_list()
        self.surf_ids, self.surf_sites = self.get_surface_sites()

        self.site_list = []
        self.populate_site_list()
        if self.label_sites:
            self.get_labels()
        if self.ignore_bridge_sites:
            self.site_list = [s for s in self.site_list if 'bridge' not in s['site']]
        self.site_list.sort(key=lambda x: x['indices'])
 
    def populate_site_list(self):
        """Find all ontop, bridge and hollow sites (3-fold and 4-fold) 
        given an input nanoparticle based on CNA analysis of the suface
        atoms and collect in a site list."""

        ss = self.surf_sites
        ssall = set(ss['all'])
        fcna = self.get_fullCNA()
        sl = self.site_list
        usi = set()  # used_site_indices
        normals_for_site = dict(list(zip(ssall, [[] for _ in ssall])))
        for surface, sites in ss.items():
            if surface == 'all':
                continue
            for s in sites:
                neighbors, _, dist2 = self.nblist.get_neighbors(s, self.r + 0.2)
                for n in neighbors:
                    si = tuple(sorted([s, n]))  # site_indices
                    if n in ssall and si not in usi:
                        # bridge sites
                        pos = np.average(self.positions[[n, s]], 0)
                        site_surf = self.get_surface_designation([s, n])
                        site = self.new_site()
                        site.update({'site': 'bridge',
                                     'surface': site_surf,
                                     'position': np.round(pos, 8),
                                     'indices': si})
                        if self.composition_effect:                         
                            symbols = [(self.symbols[i], self.numbers[i]) 
                                       for i in si]
                            comp = sorted(symbols, key=lambda x: x[1])
                            composition = ''.join([c[0] for c in comp])
                            site.update({'composition': composition})
                        sl.append(site)
                        usi.add(si)
                # Find normal
                for n, m in combinations(neighbors, 2):
                    si = tuple(sorted([s, n, m]))
                    if n in ssall and m in ssall and si not in usi:
                        angle = self.get_angle([s, n, m])
                        if self.is_eq(angle, np.pi/3.):
                            # 3-fold (fcc or hcp) site
                            normal = self.get_surface_normal([s, n, m])
                            for i in [s, n, m]:
                                normals_for_site[i].append(normal)
                            pos = np.average(self.positions[[n, m, s]], 0)
                            new_pos = pos - normal * self.r * (2./3)**(.5)

                            isubs = [a.index for a in self.ref_atoms if 
                                     np.linalg.norm(a.position - new_pos) < 0.5]
                            if not isubs:
                                this_site = 'fcc'
                            else:
                                isub = isubs[0]
                                this_site = 'hcp'
                            site_surf = 'fcc111'

                            site = self.new_site()
                            site.update({'site': this_site,
                                         'surface': site_surf,
                                         'position': np.round(pos, 8),
                                         'normal': np.round(normal, 8),
                                         'indices': si})
                            if self.composition_effect:                       
                                metals = self.metals
                                if len(metals) == 1:
                                    composition = 3*metals[0]
                                elif len(metals) == 2:
                                    ma, mb = metals[0], metals[1]
                                    symbols = [self.symbols[i] for i in si]
                                    nma = symbols.count(ma)
                                    if nma == 0:
                                        composition = 3*mb
                                    elif nma == 1:
                                        composition = ma + 2*mb
                                    elif nma == 2:
                                        composition = 2*ma + mb
                                    elif nma == 3:
                                        composition = 3*ma
                                else:
                                    nodes = self.symbols[list(si)]
                                    composition = ''.join(hash_composition(nodes))
                                site.update({'composition': composition})   

                            if this_site == 'hcp':
                                site.update({'subsurf_index': isub})
                                if self.composition_effect:
                                    site.update({'subsurf_element': 
                                                 self.symbols[isub]})
                            sl.append(site)
                            usi.add(si)

                        elif self.is_eq(angle, np.pi/2.):
                            # 4-fold hollow site
                            site_surf = 'fcc100'
                            l2 = self.r * math.sqrt(2) + 0.2
                            nebs2, _, _ = self.nblist.get_neighbors(s, l2)
                            nebs2 = [k for k in nebs2 if k not in neighbors]
                            for k in nebs2:
                                si = tuple(sorted([s, n, m, k]))
                                if k in ssall and si not in usi:
                                    d1 = self.ref_atoms.get_distance(n, k)
                                    if self.is_eq(d1, self.r, 0.2):
                                        d2 = self.ref_atoms.get_distance(m, k)
                                        if self.is_eq(d2, self.r, 0.2):
                                            # 4-fold hollow site found
                                            normal = self.get_surface_normal([s, n, m])
                                            # Save the normals now and add them to the site later
                                            for i in [s, n, m, k]:
                                                normals_for_site[i].append(normal)
                                            ps = self.positions[[n, m, s, k]]
                                            pos = np.average(ps, 0)
 
                                            site = self.new_site()
                                            site.update({'site': '4fold',
                                                         'surface': site_surf,
                                                         'position': np.round(pos, 8),
                                                         'normal': np.round(normal, 8),
                                                         'indices': si})
                                            if self.composition_effect:
                                                metals = self.metals 
                                                if len(metals) == 1:
                                                    composition = 4*metals[0]
                                                elif len(metals) == 2:
                                                    ma, mb = metals[0], metals[1]
                                                    symbols = [self.symbols[i] for i in si]
                                                    nma = symbols.count(ma)
                                                    if nma == 0:
                                                        composition = 4*mb
                                                    elif nma == 1:
                                                        composition = ma + 3*mb
                                                    elif nma == 2:
                                                        opp = max(list(si[1:]), key=lambda x: 
                                                              np.linalg.norm(self.positions[x]
                                                              - self.positions[si[0]])) 
                                                        if self.symbols[opp] == self.symbols[si[0]]:
                                                            composition = ma + mb + ma + mb 
                                                        else:
                                                            composition = 2*ma + 2*mb 
                                                    elif nma == 3:
                                                        composition = 3*ma + mb
                                                    elif nma == 4:
                                                        composition = 4*ma
                                                else:
                                                    opp = max(list(si[1:]), key=lambda x:
                                                              np.linalg.norm(self.positions[x]
                                                              - self.positions[si[0]]))
                                                    nni = [i for i in si[1:] if i != opp]
                                                    nodes = self.symbols[[si[0], nni[0], opp, nni[1]]]
                                                    composition = ''.join(hash_composition(nodes))
                                                site.update({'composition': composition})    

                                            new_pos = pos - normal * self.r * (2./3)**(.5)
                                            isub = min(range(len(self.atoms)), key=lambda x:                                            
                                                   np.linalg.norm(self.positions[x] - new_pos))  
                                            site.update({'subsurf_index': isub})
                                            if self.composition_effect:
                                                site.update({'subsurf_element': 
                                                             self.symbols[isub]})
                                            sl.append(site)
                                            usi.add(si)

                # ontop sites
                site = self.new_site()
                site.update({'site': 'ontop', 
                             'surface': surface,
                             'position': np.round(self.positions[s], 8),
                             'indices': (s,)})
                if self.composition_effect:
                    site.update({'composition': self.symbols[s]})
                sl.append(site)
                usi.add((s))

        # Add 6-fold sites if allowed
        if self.allow_6fold:
            dh = 2. * self.r / 5.
            subsurf_ids = self.get_subsurface()
        for t in sl:
            # Add normals to ontop sites
            if t['site'] == 'ontop':
                n = np.average(normals_for_site[t['indices'][0]], 0)
                t['normal'] = np.round(n / np.linalg.norm(n), 8)
            # Add normals to bridge sites
            elif t['site'] == 'bridge':
                normals = []
                for i in t['indices']:
                    normals.extend(normals_for_site[i])
                n = np.average(normals, 0)
                t['normal'] = np.round(n / np.linalg.norm(n), 8)
            # Add subsurf sites
            if self.allow_6fold:
                if t['site'] == 'fcc':  
                    site = t.copy()
                    subpos = t['position'] - t['normal'] * dh                                   
                    def get_squared_distance(x):
                        return np.sum((self.positions[x] - subpos)**2)
                    subsi = sorted(sorted(subsurf_ids, key=get_squared_distance)[:3])     
                    si = site['indices']
                    site.update({'site': '6fold',      
                                 'position': np.round(subpos, 8),
                                 'indices': tuple(sorted(si+tuple(subsi)))})      
                    if self.composition_effect:
                        metals = self.metals
                        comp = site['composition']
                        if len(metals) == 1:
                            composition = ''.join([comp, 3*metals[0]])
                        elif len(metals) == 2: 
                            ma, mb = metals[0], metals[1]
                            subsyms = [self.symbols[subi] for subi in subsi]
                            nma = subsyms.count(ma)
                            if nma == 0:
                                composition = ''.join([comp, 3*mb])
                            elif nma == 1:
                                ia = subsi[subsyms.index(ma)]
                                subpos = self.positions[ia]
                                if self.symbols[max(si, key=get_squared_distance)] == ma:
                                    composition = ''.join([comp, 2*mb + ma])
                                else:
                                    composition = ''.join([comp, ma + 2*mb])
                            elif nma == 2:
                                ib = subsi[subsyms.index(mb)]
                                subpos = self.positions[ib]
                                if self.symbols[max(si, key=get_squared_distance)] == mb:
                                    composition = ''.join([comp, 2*ma + mb])
                                else:
                                    composition = ''.join([comp, mb + 2*ma])
                            elif nma == 3:
                                composition = ''.join([comp, 3*ma])
                        else:
                            endsym = re.findall('[A-Z][^A-Z]*', comp)[-1]
                            subpos = [self.positions[i] for i in si if 
                                      self.symbols[i] == endsym][0]
                            nodes = self.symbols[sorted(subsi, key=get_squared_distance)]
                            composition = comp + ''.join(hash_composition(nodes))
                        site.update({'composition': composition})
                    sl.append(site)
                    usi.add(si) 

    def get_site(self, indices):
        """Get information of a site given its atom indices.
        
        Parameters
        ----------
        indices : list or tuple
            The indices of the atoms that contribute to the site.
        
        """

        indices = indices if is_list_or_tuple(indices) else [indices]
        indices = tuple(sorted(indices))
        st = next((s for s in self.site_list if 
                   s['indices'] == indices), None)
        return st 

    def get_sites(self, site=None,
                  surface=None, 
                  composition=None, 
                  subsurf_element=None):
        """Get information of all sites.
                                                                     
        Parameters                                                   
        ----------                                                   
        site : str, default None
            Only return sites that belongs to this site type.

        surface : str, default None
            Only return sites that are on this surface.

        composition : str, default None
            Only return sites that have this composition.

        subsurf_element : str, default None
            Only return sites that have this subsurface element.
                                                                     
        """                                                          

        all_sites = self.site_list
        if site is not None:
            all_sites = [s for s in all_sites if s['site'] == site] 
        if surface is not None:
            all_sites = [s for s in all_sites if s['surface'] == surface] 
        if composition is not None: 
            if '-' in composition or len(list(Formula(composition))) == 6:
                scomp = composition
            else:
                comp = re.findall('[A-Z][^A-Z]*', composition)
                if len(comp) != 4:
                    scomp = ''.join(sorted(comp, key=lambda x: 
                                           atomic_numbers[x]))
                else:
                    if comp[0] != comp[2]:
                        scomp = ''.join(sorted(comp, key=lambda x: 
                                               atomic_numbers[x]))
                    else:
                        if atomic_numbers[comp[0]] > atomic_numbers[comp[1]]:
                            scomp = comp[1]+comp[0]+comp[3]+comp[2]
                        else:
                            scomp = ''.join(comp)

            all_sites = [s for s in all_sites if s['composition'] == scomp]
        if subsurf_element is not None:
            all_sites = [s for s in all_sites if s['subsurf_element'] 
                         == subsurf_element]

        return all_sites

    def get_unique_sites(self, unique_composition=False,         
                         unique_subsurf=False,
                         return_signatures=False,
                         return_site_indices=False,
                         site_list=None):
        """Get all symmetry-inequivalent adsorption sites (one
        site for each type).
        
        Parameters
        ----------
        unique_composition : bool, default False
            Take site composition into consideration when 
            checking uniqueness.

        unique_subsurf : bool, default False
            Take subsurface element into consideration when 
            checking uniqueness. Could be important for 
            surfaces like fcc100.

        return_signatures : bool, default False           
            Whether to return the unique signatures of the
            sites instead.

        return_site_indices: bool, default False
            Whether to return the indices of each unique 
            site (in the site list).                     

        """

        if site_list is None:
            sl = self.site_list
        else:
            sl = site_list
        key_list = ['site', 'surface']
        if unique_composition:
            if not self.composition_effect:
                raise ValueError('the site list does not include '
                                 + 'information of composition')
            key_list.append('composition')
            if unique_subsurf:
                key_list.append('subsurf_element') 
        else:
            if unique_subsurf:
                raise ValueError('to include the subsurface element, ' +
                                 'unique_composition also need to be set to True')    

        if return_signatures:
            sklist = sorted([[s[k] for k in key_list] for s in sl])
            return sorted(list(sklist for sklist, _ in groupby(sklist)))
        else:
            seen_tuple = []
            uni_sites = []
            for i, s in enumerate(sl):
                sig = tuple(s[k] for k in key_list)
                if sig not in seen_tuple:
                    seen_tuple.append(sig)
                    if return_site_indices:
                        s = i 
                    uni_sites.append(s)
            return uni_sites                        

    def get_labels(self):
        # Assign labels
        for st in self.site_list:
            if self.composition_effect:
                signature = [st['site'], st['surface'], st['composition']]            
            else:
                signature = [st['site'], st['surface']]
            stlab = self.label_dict['|'.join(signature)]
            st['label'] = stlab                                                   

    def new_site(self):
        return {'site': None, 'surface': None, 'position': None, 
                'normal': None, 'indices': None, 'composition': None,
                'subsurf_index': None, 'subsurf_element': None, 'label': None}

    def mapping(self, atoms):
        """Map the nanoparticle into a surrogate nanoparticle for code
        versatility."""

        ref_atoms = atoms.copy()
        pm = self.surrogate_metal
        if pm is None:
            common_metal = Counter(self.atoms.symbols).most_common(1)[0][0]
            if common_metal in ['Ni', 'Cu', 'Pd', 'Ag', 'Pt', 'Au']:
                ref_symbol = common_metal
            else:
                ref_symbol = 'Au' if len(atoms) > 300 else 'Cu'
        else:
            ref_symbol = pm
        for a in ref_atoms:
            a.symbol = ref_symbol

        ref_atoms.calc = asapEMT()
        opt = FIRE(ref_atoms, logfile=None)
        opt.run(fmax=0.1)
        ref_atoms.calc = None              

        return ref_atoms

    def get_two_vectors(self, indices):
        p1 = self.positions[indices[1]]
        p2 = self.positions[indices[2]]
        vec1 = p1 - self.positions[indices[0]]
        vec2 = p2 - self.positions[indices[0]]
        return vec1, vec2

    def is_eq(self, v1, v2, eps=0.1):
        if abs(v1 - v2) < eps:
            return True
        else:
            return False

    def get_surface_normal(self, indices): 
        """Get the surface normal vector of the plane from the indices 
        of 3 atoms that forms to that plane.                                    
                                                                    
        Parameters
        ----------
        indices : list of tuple
            The indices of the atoms that forms the plane.
        
        """
        vec1, vec2 = self.get_two_vectors(indices)
        n = np.cross(vec1, vec2)
        l = math.sqrt(n @ n.conj())
        new_pos = self.positions[indices[0]] + self.r * n / l
        # Add support for having adsorbates on the particles already
        # by putting in elements to check for in the function below
        j = 2 * int(self.no_atom_too_close_to_pos(new_pos, (5./6)*self.r)) - 1

        return j * n / l

    def get_angle(self, indices):
        vec1, vec2 = self.get_two_vectors(indices)
        p = (vec1 @ vec2)/(np.linalg.norm(vec1) * np.linalg.norm(vec1))
        return np.arccos(np.clip(p, -1,1))

    def no_atom_too_close_to_pos(self, pos, mindist):              
        """Returns True if no atoms are closer than mindist to pos,
        otherwise False.

        Parameters
        ----------
        pos : numpy.array
            The position to be checked.

        mindist : float
            The minimum distance (in Angstrom) that is not considered 
            as too close.

        """
        dists = [np.linalg.norm(atom.position - pos) > mindist
                 for atom in self.ref_atoms]
        return all(dists)                                                       

    def get_surface_sites(self): 
        """Returns the indices of the surface atoms and a dictionary 
        with all the surface designations."""

        surf_sites = {'all': [],
                      'fcc111': [],
                      'fcc100': [],
                      'edge': [],
                      'vertex': [],}
        fcna = self.get_fullCNA()
        site_dict = self.site_dict
        surf_ids = []

        for i in range(len(self.atoms)):
#            if i in [284, 310]:
#                print(fcna[i])
            if sum(fcna[i].values()) < 12:
                surf_sites['all'].append(i)
                if str(fcna[i]) not in site_dict:
                    # The structure is distorted from the original, giving
                    # a larger cutoff should overcome this problem
                    r = self.r + self.tol
                    fcna = self.get_fullCNA(rCut=r)
                if str(fcna[i]) not in site_dict:
                    # If this does not solve the problem we probably have a
                    # reconstruction of the surface and will leave this
                    # atom unused this time
                    continue
                surf_ids.append(i)
                surf_sites[site_dict[str(fcna[i])]].append(i)
        return surf_ids, surf_sites  

    def get_subsurface(self):
        """Returns the indices of the subsurface atoms."""

        notsurf = [a.index for a in self.atoms if a.index not in self.surf_ids]
        subfcna = FullCNA(self.ref_atoms[notsurf]).get_normal_cna() 
        
        return [idx for i, idx in enumerate(notsurf) if 
                sum(subfcna[i].values()) < 12]

    def make_fullCNA(self, rCut=None):                  
        if rCut not in self.fullCNA:
            self.fullCNA[rCut] = FullCNA(self.ref_atoms, rCut=rCut).get_normal_cna()

    def get_fullCNA(self, rCut=None):
        """Get the CNA signatures of all atoms by asap3 full CNA 
        analysis.

        Parameters
        ----------
        rCut : float, default None
            The cutoff radius in Angstrom. If not specified, the 
            asap3 CNA analysis will use a reasonable cutoff based 
            on the crystalline lattice constant of the material.

        """

        if rCut not in self.fullCNA:
            self.make_fullCNA(rCut=rCut)
        return self.fullCNA[rCut]

    def make_neighbor_list(self, rMax=10.):
        """Get an asap3 neighborlist.

        Parameters
        ----------
        rMax : float, default 10.
            The maximum cutoff radius in Angstrom. 

        """

        self.nblist = FullNeighborList(rCut=rMax, atoms=self.ref_atoms)

    def get_connectivity(self):                                      
        """Get the adjacency matrix."""

        nbslist = neighbor_shell_list(self.ref_atoms, 0.3, neighbor_number=1)
        return get_adj_matrix(nbslist)                  

    def get_site_dict(self):
        icosa_dict = {                                                                                     
            # Triangle sites on outermost shell -- Icosa, Cubocta, Deca, Tocta
            str({(3, 1, 1): 6, (4, 2, 1): 3}): 'fcc111',
            'fcc111': [str({(3, 1, 1): 6, (4, 2, 1): 3})],
            # Edge sites on outermost shell -- Icosa
            str({(3, 1, 1): 4, (3, 2, 2): 2, (4, 2, 2): 2}): 'edge',
            'edge': [str({(3, 1, 1): 4, (3, 2, 2): 2, (4, 2, 2): 2})],
            # Vertice sites on outermost shell -- Icosa, Deca
            str({(3, 2, 2): 5, (5, 5, 5): 1}): 'vertex',
            'vertex': [str({(3, 2, 2): 5, (5, 5, 5): 1})],
        }
        
        cubocta_dict = {
            # Edge sites on outermost shell -- Cubocta, Tocta
            str({(2, 1, 1): 3, (3, 1, 1): 2, (4, 2, 1): 2}): 'edge',
            'edge': [str({(2, 1, 1): 3, (3, 1, 1): 2, (4, 2, 1): 2})],
            # Square sites on outermost shell -- Cubocta, Deca, Tocta
            str({(2, 1, 1): 4, (4, 2, 1): 4}): 'fcc100',
            'fcc100': [str({(2, 1, 1): 4, (4, 2, 1): 4})],
            # Vertice sites on outermost shell -- Cubocta
            str({(2, 1, 1): 4, (4, 2, 1): 1}): 'vertex',
            'vertex': [str({(2, 1, 1): 4, (4, 2, 1): 1})],
            # Triangle sites on outermost shell -- Icosa, Cubocta, Deca, Tocta
            str({(3, 1, 1): 6, (4, 2, 1): 3}): 'fcc111',
            'fcc111': [str({(3, 1, 1): 6, (4, 2, 1): 3})],
        }
        
        mdeca_dict = {
            # Edge sites (111)-(111) on outermost shell -- Deca
            str({(3, 1, 1): 4, (3, 2, 2): 2, (4, 2, 2): 2}): 'edge',
            'edge': [str({(3, 1, 1): 4, (3, 2, 2): 2, (4, 2, 2): 2}), 
                     str({(2, 1, 1): 3, (3, 1, 1): 2, (4, 2, 1): 2}), 
                     str({(2, 0, 0): 2, (3, 1, 1): 4, (4, 2, 1): 1})],
            # Edge sites (111)-(100) on outermost shell -- Deca
            str({(2, 1, 1): 3, (3, 1, 1): 2, (4, 2, 1): 2}): 'edge',
            # Edge sites (111)-(111)notch on outermost shell -- Deca
            str({(2, 0, 0): 2, (3, 1, 1): 4, (4, 2, 1): 1}): 'edge',
            # Square sites on outermost shell -- Cubocta, Deca, Tocta
            str({(2, 1, 1): 4, (4, 2, 1): 4}): 'fcc100',
            'fcc100': [str({(2, 1, 1): 4, (4, 2, 1): 4})],
            # Vertice sites on outermost shell -- Icosa, Deca
            str({(3, 2, 2): 5, (5, 5, 5): 1}): 'vertex',
            'vertex': [str({(3, 2, 2): 5, (5, 5, 5): 1}), 
                       str({(2, 0, 0): 1, (2, 1, 1): 2, (3, 1, 1): 2, (4, 2, 1): 1}), 
                       str({(2, 0, 0): 2, (3, 0, 0): 1, (3, 1, 1): 2, (3, 2, 2): 1, 
                            (4, 2, 2): 1})],
            # Vertice sites A on outermost shell -- Mdeca
            str({(2, 0, 0): 1, (2, 1, 1): 2, (3, 1, 1): 2, (4, 2, 1): 1}): 'vertex',
            # Vertice sites B on outermost shell -- Mdeca
            str({(2, 0, 0): 2, (3, 0, 0): 1, (3, 1, 1): 2, 
                 (3, 2, 2): 1, (4, 2, 2): 1}): 'vertex',
            # Triangle (pentagon) sites on outermost shell -- Icosa, Cubocta, Deca, Tocta
            str({(3, 1, 1): 6, (4, 2, 1): 3}): 'fcc111',
            'fcc111': [str({(3, 1, 1): 6, (4, 2, 1): 3}), 
                       str({(3, 0, 0): 2, (3, 1, 1): 4, (4, 2, 1): 2, (4, 2, 2): 2})],
            # Triangle (pentagon) notch sites on outermost shell -- Deca
            str({(3, 0, 0): 2, (3, 1, 1): 4, (4, 2, 1): 2, (4, 2, 2): 2}): 'fcc111',
        }
        
        tocta_dict = {
            # Edge sites on outermost shell -- Cubocta, Tocta
            str({(2, 1, 1): 3, (3, 1, 1): 2, (4, 2, 1): 2}): 'edge',
            'edge': [str({(2, 1, 1): 3, (3, 1, 1): 2, (4, 2, 1): 2}), 
                     str({(2, 0, 0): 2, (3, 1, 1): 4, (4, 2, 1): 1})],
            # Edge sites (111)-(111) on outermost shell -- Octa
            str({(2, 0, 0): 2, (3, 1, 1): 4, (4, 2, 1): 1}): 'edge',
            # Square sites on outermost shell -- Cubocta, Deca, Tocta
            str({(2, 1, 1): 4, (4, 2, 1): 4}): 'fcc100',
            'fcc100': [str({(2, 1, 1): 4, (4, 2, 1): 4})],
            # Vertice sites on outermost shell -- Tocta
            str({(2, 0, 0): 1, (2, 1, 1): 2, (3, 1, 1): 2, (4, 2, 1): 1}): 'vertex',
            'vertex': [str({(2, 0, 0): 1, (2, 1, 1): 2, (3, 1, 1): 2, (4, 2, 1): 1})],
            # Triangle (pentagon) sites on outermost shell -- Icosa, Cubocta, Deca, Octa
            str({(3, 1, 1): 6, (4, 2, 1): 3}): 'fcc111',
            'fcc111': [str({(3, 1, 1): 6, (4, 2, 1): 3})],
        }
        
        fcna = self.get_fullCNA()
        icosa_weight = cubocta_weight = mdeca_weight = tocta_weight = 0
        for s in fcna:
            if str(s) in icosa_dict:
                icosa_weight += 1
            if str(s) in cubocta_dict:
                cubocta_weight += 1
            if str(s) in mdeca_dict:
                mdeca_weight += 1
            if str(s) in tocta_dict:
                tocta_weight += 1
        full_weights = [icosa_weight, cubocta_weight, 
                        mdeca_weight, tocta_weight]
        if icosa_weight == max(full_weights):
            return icosa_dict
        elif cubocta_weight == max(full_weights):
            return cubocta_dict
        elif tocta_weight == max(full_weights):
            return tocta_dict
        else:
            return mdeca_dict

    def set_first_neighbor_distance_from_rdf(self, rMax=10, nBins=200):
        atoms = self.ref_atoms.copy()
        for j, L in enumerate(list(atoms.cell.diagonal())):
            if L <= 10:
                atoms.cell[j][j] = 12 
        _rdf = rdf.RadialDistributionFunction(atoms, rMax, nBins).get_rdf()
        x = (np.arange(nBins) + 0.5) * rMax / nBins
        _rdf *= x**2
        diff_rdf = np.gradient(_rdf)

        i = 0
        while diff_rdf[i] >= 0:
            i += 1
        self.r = x[i]

    def get_surface_designation(self, indices):                                 
        fcna = self.get_fullCNA()
        sd = self.site_dict
        if len(indices) == 1:
            s = indices[0]
            return sd[str(fcna[s])]
        elif len(indices) == 2:
            if str(fcna[indices[0]]) not in sd or str(fcna[indices[1]]) not in sd:
               # for s in [indices[0], indices[1]]:
               #     scna = str(fcna[s])
               #     if scna not in sd:
               #         print('CNA {} is not supported.'.format(scna))
                return 'unknown'
            s0 = sd[str(fcna[indices[0]])]
            s1 = sd[str(fcna[indices[1]])]
            ss01 = tuple(sorted([s0, s1]))
            if ss01 in [('edge', 'edge'), 
                        ('edge', 'vertex'),
                        ('vertex', 'vertex')]:
                return 'edge'
            elif ss01 in [('fcc111', 'vertex'), 
                          ('edge', 'fcc111'), 
                          ('fcc111', 'fcc111')]:
                return 'fcc111'
            elif ss01 in [('fcc100', 'vertex'), 
                          ('edge', 'fcc100'), 
                          ('fcc100', 'fcc100')]:
                return 'fcc100'
        elif len(indices) == 3:
            return 'fcc111'

    def get_graph(self, return_adj_matrix=False):                             
        """Get the graph representation of the slab.

        Parameters
        ----------
        return_adj_matrix : bool, default False
            Whether to return adjacency matrix instead of the networkx.Graph 
            object.

        """

        cm = self.get_connectivity()
        if return_adj_matrix:
            return cm
        
        G = nx.Graph()                               
        symbols = self.symbols                               
        G.add_nodes_from([(i, {'symbol': symbols[i]}) 
                          for i in range(len(symbols))])
        rows, cols = np.where(cm == 1)
        edges = zip(rows.tolist(), cols.tolist())
        G.add_edges_from(edges)

        return G

    def get_neighbor_site_list(self, dx=0.1, neighbor_number=1, 
                               radius=None, span=True, unique=False, 
                               unique_composition=False,
                               unique_subsurf=False):           
        """Returns the site_list index of all neighbor shell sites 
        for each site.

        Parameters
        ----------
        dx : float, default 0.1
            Buffer to calculate nearest neighbor site pairs.

        neighbor_number : int, default 1
            Neighbor shell number.

        radius : float, default None
            The radius that defines site a is a neighbor of site b.
            This serves as an alternative to neighbor_number.      

        span : bool, default True
            Whether to include all neighbors sites spanned within 
            the shell.

        unique : bool, default False
            Whether to discard duplicate types of neighbor sites.

        """

        sl = self.site_list
        poss = np.asarray([s['position'] for s in sl])
        statoms = Atoms('X{}'.format(len(sl)), positions=poss,
                        cell=self.cell, pbc=self.pbc)
        if radius is not None:                                                           
            nbslist = neighbor_shell_list(statoms, dx, neighbor_number=1,
                                          mic=False, radius=radius, span=span)
            if unique:
                for i in range(len(nbslist)):
                    nbsids = nbslist[i]
                    tmpids = self.get_unique_sites(unique_composition, unique_subsurf,
                                                   return_site_indices=True,
                                                   site_list=[sl[ni] for ni in nbsids])
                    nbsids = [nbsids[j] for j in tmpids]
                    nbslist[i] = nbsids
        else:
            D = statoms.get_all_distances(mic=False)
            nbslist = {}
            for i, row in enumerate(D):
                argsort = np.argsort(row)
                row = row[argsort]
                res = np.split(argsort, np.where(np.abs(np.diff(row)) > dx)[0] + 1)
                if span:
                    nbsids = sorted([n for nn in range(1, neighbor_number + 1) 
                                     for n in list(res[nn])])
                else:
                    nbsids = sorted(res[neighbor_number])
                if unique:
                    tmpids = self.get_unique_sites(unique_composition, unique_subsurf,
                                                   return_site_indices=True, 
                                                   site_list=[sl[ni] for ni in nbsids])
                    nbsids = [nbsids[j] for j in tmpids]
                nbslist[i] = nbsids

        return nbslist

    def update(self, atoms, update_composition=False):                 
        """Update the position and composition of each adsorption site 
        given an updated atoms object. Please only use this when the 
        indexing of the atoms object is preserved. Useful for updating
        adsorption sites e.g. after geometry optimization.
        
        Parameters
        ----------
        atoms : ase.Atoms object
            The updated atoms object. 

        update_composition : bool, default False
            Whether to update the composition as well. It is recommended
            to only set update_composition=True if the composition of 
            the surface is not fixed.  

        """ 

        sl = self.site_list
        for st in sl:
            si = list(st['indices'])
            newpos = np.average(atoms.positions[si], 0) 
            st['position'] = np.round(newpos, 8)
            if update_composition:
                newcomp = ''.join(sorted(atoms.symbols[si], key=
                                         lambda x: atomic_numbers[x]))
                st['composition'] = newcomp                           


def group_sites_by_facet(atoms, sites, all_sites=None):            
    """A function that uses networkx to group one set of sites by
    geometrical facets of the nanoparticle. Different geometrical
    facets can have the same surface type. The function returns a
    list of lists, each contains sites on a same geometrical facet.

    Parameters
    ----------
    atoms : ase.Atoms object
        The atoms object must be a non-periodic nanoparticle.
        Accept any ase.Atoms object. No need to be built-in.

    sites : list of dicts
        The adsorption sites to be grouped by geometrical facet.

    all_sites : list of dicts, default None
        The list of all sites. Provide this to make the grouping
        much faster. Useful when the function is called many times.

    Example
    -------
    The following example shows how to group all fcc sites of an 
    icosahedral nanoparticle by its 20 geometrical facets:

        >>> from acat.adsorption_sites import ClusterAdsorptionSites
        >>> from acat.adsorption_sites import group_sites_by_facet
        >>> from ase.cluster import Icosahedron
        >>> atoms = Icosahedron('Pt', noshells=5)
        >>> atoms.center(vacuum=5.)
        >>> cas = ClusterAdsorptionSites(atoms)
        >>> all_sites = cas.get_sites()
        >>> fcc_sites = [s for s in all_sites if s['site'] == 'fcc']
        >>> groups = group_sites_by_facet(atoms, fcc_sites, all_sites)         
        >>> print(len(groups))

    Output:

    .. code-block:: python

        20

    """
                                                                     
    # Find all indices of vertex and edge sites
    if not all_sites:
        cas = ClusterAdsorptionSites(atoms)
        all_sites = cas.site_list
    ve_indices = [s['indices'] for s in all_sites if 
                  s['site'] == 'ontop' and 
                  s['surface'] in ['vertex', 'edge']]
    unique_ve_indices = set(list(sum(ve_indices, ())))
     
    G = nx.Graph()
    for site in sites:
        indices = site['indices']
        reduced_indices = tuple(i for i in indices if i 
                                not in unique_ve_indices)
        site['reduced_indices'] = reduced_indices
        nx.add_path(G, reduced_indices)
    components = list(nx.connected_components(G))
    groups = []
    for component in components:
        group = []
        for path in [s['reduced_indices'] for s in sites]:
            if component.issuperset(path):
                group.append(path)
        groups.append(group)
    grouped_sites = defaultdict(list)
    for site in sites:
        for group in groups:
            if site['reduced_indices'] in group:
                grouped_sites[groups.index(group)] += [site]
                                                                     
    return grouped_sites


class SlabAdsorptionSites(object):
    """Base class for identifying adsorption sites on a surface slab.
    Support 20 common surfaces: fcc100, fcc111, fcc110, fcc211,
    fcc221, fcc311, fcc322, fcc331, fcc332, bcc100, bcc111, bcc110,
    bcc210, bcc211, bcc310, hcp0001, hcp10m10t, hcp10m10h, 
    hcp10m11, hcp10m12.

    The information of each site is stored in a dictionary with the 
    following keys:

    **'site'**: the site type, support 'ontop', 'bridge', 'longbridge', 
    'shortbridge', 'fcc', 'hcp', '3fold', '4fold', '5fold', '6fold'.

    **'surface'**: the surface type (crystal structure + Miller indices) 
    of the slab. Support 20 surfaces as listed above.

    **'morphology'**: the local surface morphology of the site. Support
    'step', 'terrace', 'corner', 'sc-tc-x', 'tc-cc-x', 'sc-cc-x'.
    'sc', 'tc' and 'cc' represents step chain, terrace chain and corner, 
    respectively. 'x' is the Bravais lattice that connects the 2 chains,
    e.g. 'h' = hexagonal, 't' = 'tetragonal', 'o' = 'orthorhombic'.

    **'position'**: the 3D Cartesian coordinate of the site saved as a
    numpy array.

    **'normal'**: the surface normal vector of the site saved as a numpy
    array.

    **'indices'**: the indices of the atoms that constitute the site.

    **'composition'**: the elemental composition of the site. Always in 
    the lowest lexicographical order.

    **'subsurf_index'**: the index of the subsurface atom underneath an
    hcp or 4fold site.

    **'subsurf_element'**: the element of the subsurface atom underneath
    an hcp or 4fold site

    **'label'**: the numerical label assigned to the site if label_sites
    is set to True.

    Parameters
    ----------
    atoms : ase.Atoms object
        The atoms object must be a periodic surface slab with at 
        least 3 layers (e.g. all surface atoms make up one layer). 
        Accept any ase.Atoms object. No need to be built-in.

    surface : str
        The surface type (crystal structure + Miller indices).

    allow_6fold : bool, default False
        Whether to allow the adsorption on 6-fold subsurf sites 
        underneath fcc hollow sites.

    composition_effect : bool, default False
        Whether to consider sites with different elemental 
        compositions as different sites. It is recommended to 
        set composition_effect=False for monometallics.        

    both_sides : bool, default False
        Whether to consider sites on both top and bottom sides
        of the slab.

    ignore_bridge_sites : bool, default False
        Whether to ignore bridge sites.

    label_sites : bool, default False
        Whether to assign a numerical label to each site.
        Labels for different sites are listed in acat.labels.
        Use the bimetallic labels if composition_effect=True,
        otherwise use the monometallic labels.

    surrogate_metal : str, default None
        The code is parameterized w.r.t. pure transition metals.
        The generalization of the code is achieved by mapping all 
        input atoms to a surrogate transition metal that is 
        supported by the asap3.EMT calculator (Ni, Cu, Pd, Ag, Pt 
        or Au). Try changing the surrogate metal when the site 
        identification is not satisfying. When the cell is small, 
        Cu is normally the better choice, while the Pt and Au 
        should be good for larger cells. If no surrogate metal is
        provided, but the majority of the slab is a metal supported     
        by asap3.EMT, the surrogate metal will be set to that metal 
        automatically.

    optimize_surrogate_cell : bool, default False
        Whether to also optimize the cell during the optimization
        of the surrogate slab. Useful for generalizing the code for
        alloy slabs of various compositions and lattice constants.
        Recommand to set to True if the surrogate metal is very 
        different from the composition of the input slab.

    tol : float, default 0.5
        The tolerence of neighbor distance (in Angstrom).
        Might be helpful to adjust this if the site identification 
        is not satisfying. The default 0.5 is usually good enough.

    Example
    -------
    The following example illustrates the most important use of a
    `SlabAdsorptionSites` object - getting all adsorption sites:

        >>> from acat.adsorption_sites import SlabAdsorptionSites
        >>> from ase.build import fcc211
        >>> atoms = fcc211('Cu', (3, 3, 4), vacuum=5.)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Au' 
        >>> atoms.center()
        >>> sas = SlabAdsorptionSites(atoms, surface='fcc211',
        ...                           allow_6fold=False,
        ...                           composition_effect=True,
        ...                           label_sites=True)
        >>> sites = sas.get_sites()
        >>> print(sites[-1])

    Output:

    .. code-block:: python

        {'site': 'hcp', 'surface': 'fcc211', 'morphology': 'sc-tc-h', 
         'position': array([ 4.51584136,  0.63816387, 12.86014042]), 
         'normal': array([-0.33333333, -0.        ,  0.94280904]), 
         'indices': (0, 2, 3), 'composition': 'CuAuAu', 
         'subsurf_index': 9, 'subsurf_element': 'Cu', 'label': 28}

    """

    def __init__(self, atoms, surface, 
                 allow_6fold=False, 
                 composition_effect=False, 
                 both_sides=False,
                 ignore_bridge_sites=False,
                 label_sites=False,
                 surrogate_metal=None,
                 optimize_surrogate_cell=False,
                 tol=.5, _allow_expand=True):

        assert True in atoms.pbc, 'the cell must be periodic in at least one direction'   
        warnings.filterwarnings('ignore', category=RuntimeWarning)
        warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)

        atoms = atoms.copy() 
        ptp = np.ptp(atoms.positions[:, 2]) 
        if np.linalg.norm(atoms.cell[2]) - ptp < 10.:
            atoms.cell[2][2] = ptp + 10.
        del atoms.constraints
        del atoms[[a.index for a in atoms if 'a' not in reference_states[a.number]]]
        del atoms[[a.index for a in atoms if a.symbol in adsorbate_elements]]

        self.atoms = atoms
        self.positions = atoms.positions 
        self.symbols = atoms.symbols
        self.numbers = atoms.numbers
        self.indices = list(range(len(self.atoms)))
        self.surface = surface
        self.surrogate_metal = surrogate_metal
        self.optimize_surrogate_cell = optimize_surrogate_cell

        self.ref_atoms, self.delta_positions = self.mapping(atoms) 
        self.cell = atoms.cell
        self.pbc = atoms.pbc
        self.metals = sorted(list(set(atoms.symbols)), 
                             key=lambda x: atomic_numbers[x])
        self.allow_6fold = allow_6fold
        self.composition_effect = composition_effect
        self.both_sides = both_sides
        self.ignore_bridge_sites = ignore_bridge_sites
        self.label_sites = label_sites

        if self.composition_effect:
            if len(self.metals) <= 2:
                if len(self.metals) == 1:
                    self.metals *= 2
                self.label_dict = get_bimetallic_slab_labels(self.surface, self.metals)
            else:
                self.label_dict = get_multimetallic_slab_labels(self.surface, self.metals)
        else:
            self.label_dict = get_monometallic_slab_labels(self.surface)    
        self.tol = tol 
        self._allow_expand = _allow_expand

        self.make_neighbor_list(neighbor_number=1) 
        self.adj_matrix = self.get_connectivity()         
        self.surf_ids, self.subsurf_ids = self.get_termination() 

        self.site_list = []
        self.populate_site_list()
        self.postprocessing()        
        self.site_list.sort(key=lambda x: x['indices'])
        
    def populate_site_list(self, cutoff=5.):        
        """Find all ontop, bridge and hollow sites (3-fold and 4-fold) 
        given an input slab based on Delaunay triangulation of the 
        surface atoms in a supercell and collect in a site list.

        Parameters
        ----------
        cutoff : float, default 5.
            Radius of maximum atomic bond distance to consider.

        """

        top_indices = self.surf_ids
        sl = self.site_list
        normals_for_site = dict(list(zip(top_indices, 
                            [[] for _ in top_indices])))
        if self.optimize_surrogate_cell:
            ref_cell = self.ref_atoms.cell
        else:
            ref_cell = self.cell
        usi = set() # used_site_indices
        cm = self.adj_matrix

        # Sort top indicies by z coordinates to identify step / terrace / corner
        sorted_top_indices = sorted(top_indices, key=lambda x: self.positions[x,2])
        ntop = len(top_indices)
        for i, s in enumerate(sorted_top_indices):
            if self.surface in ['fcc111','fcc100','bcc100','bcc110','hcp0001']:
                morphology = 'terrace'
            elif self.surface in ['fcc211','fcc322','fcc221','fcc332','bcc111','bcc210','hcp10m12']:
                if i < ntop / 3:
                    morphology = 'corner'
                elif i >= ntop * 2 / 3:
                    morphology = 'step'
                else:
                    morphology = 'terrace'
            else:
                if i < ntop / 2:
                    morphology = 'terrace'
                else:
                    morphology = 'step'

            si = (s,)
            site = self.new_site() 
            site.update({'site': 'ontop',
                         'surface': self.surface,
                         'morphology': morphology,
                         'position': np.round(self.positions[s], 8),
                         'indices': si})            
            if self.surface in ['fcc110','bcc211','hcp10m10h'] and morphology == 'terrace':
                site.update({'extra': np.where(cm[s]==1)[0]})
            if self.composition_effect:
                site.update({'composition': self.symbols[s]})
            sl.append(site)
            usi.add(si)

        stepids, terraceids, cornerids = set(), set(), set()
        for sit in sl:
            geo = sit['morphology']
            sid = sit['indices'][0]
            if geo == 'step':
                stepids.add(sid)
            elif geo == 'terrace':
                terraceids.add(sid)
            elif geo == 'corner':
                cornerids.add(sid)
        geo_dict = {'step': stepids, 'terrace': terraceids, 'corner': cornerids}

        if self.surface in ['fcc110','bcc211','hcp10m10h']:   
            for st in sl:
                if 'extra' in st:
                    si = st['indices']
                    extra = st['extra']
                    extraids = [e for e in extra if e in self.surf_ids
                                and e not in geo_dict[st['morphology']]]
                    #if len(extraids) < 4:    
                    #    warnings.warn('Cannot identify other 4 atoms of 5-fold site {}'.format(si))
                    if len(extraids) > 4:
                        extraids = sorted(extraids, key=lambda x: get_mic(                
                                   self.ref_atoms.positions[x], refpos, ref_cell,
                                   return_squared_distance=True))[:4] 
                    if self.composition_effect:
                        metals = self.metals
                        if len(metals) == 1:
                            composition = 4*metals[0]
                        elif len(metals) == 2: 
                            ma, mb = metals[0], metals[1]                       
                            symbols = [self.symbols[i] for i in extraids]
                            nma = symbols.count(ma)
                            if nma == 0:
                                composition = 4*mb
                            elif nma == 1:
                                composition = ma + 3*mb
                            elif nma == 2:
                                idd = sorted(extraids[1:], key=lambda x:    
                                      get_mic(self.positions[x], self.positions[extraids[0]],
                                              self.cell, return_squared_distance=True))
                                opp, close = idd[-1], idd[0]
                                if self.symbols[opp] == self.symbols[extraids[0]]:
                                    composition = ma + mb + ma + mb 
                                else:
                                    if self.symbols[close] == self.symbols[extraids[0]]:
                                        composition = 2*ma + 2*mb 
                                    else:
                                        composition = ma + 2*mb + ma
                            elif nma == 3:
                                composition = 3*ma + mb
                            elif nma == 4:
                                composition = 4*ma
                        else:
                            opp = max(list(extraids[1:]), key=lambda x:
                                      get_mic(self.positions[x], self.positions[extraids[0]],
                                              self.cell, return_squared_distance=True))
                            nni = [i for i in extraids[1:] if i != opp]
                            nodes = self.symbols[[extraids[0], nni[0], opp, nni[1]]]
                            composition = ''.join(hash_composition(nodes))
                        st['composition'] += '-{}'.format(composition) 
                    st['indices'] = tuple(sorted(list(si)+ extraids))
                    del st['extra']

        ext_index, ext_coords, _ = expand_cell(self.ref_atoms, cutoff)
        extended_top = np.where(np.in1d(ext_index, top_indices))[0]
        ext_surf_coords = ext_coords[extended_top]
        meansurfz = np.average(self.positions[self.surf_ids][:,2], 0)
        dh = abs(meansurfz - np.average(self.positions[self.subsurf_ids][:,2], 0))
#        surf_screen = np.where(abs(ext_surf_coords[:,2] - meansurfz) < 5.)
#        ext_surf_coords = ext_surf_coords[surf_screen]
        dt = scipy.spatial.Delaunay(ext_surf_coords[:,:2])
        neighbors = dt.neighbors
        simplices = dt.simplices

        bridge_positions, fold3_positions, fold4_positions = [], [], []
        bridge_points, fold3_points, fold4_points = [], [], []
         
        # Delaunay triangulation (borrow from Catkit)
        for i, corners in enumerate(simplices):
            cir = scipy.linalg.circulant(corners)
            edges = cir[:,1:]

            # Inner angle of each triangle corner
            vec = ext_surf_coords[edges.T] - ext_surf_coords[corners]
            uvec = vec.T / np.linalg.norm(vec, axis=2).T
            angles = np.sum(uvec.T[0] * uvec.T[1], axis=1)

            # Angle types
            right = np.isclose(angles, 0)
            obtuse = (angles < -1e-5)
            rh_corner = corners[right]
            edge_neighbors = neighbors[i]
            bridge = np.sum(ext_surf_coords[edges], axis=1) / 2.0

            # Looping through corners allows for elimination of
            # redundant points, identification of 4-fold hollows,
            # and collection of bridge neighbors.            
            for j, c in enumerate(corners):
                edge = sorted(edges[j])
                if edge in bridge_points:
                    continue

                # Get the bridge neighbors (for adsorption vector)
                neighbor_simplex = simplices[edge_neighbors[j]]
                oc = list(set(neighbor_simplex) - set(edge))[0]

                # Right angles potentially indicate 4-fold hollow
                potential_hollow = edge + sorted([c, oc])
                if c in rh_corner:
                    if potential_hollow in fold4_points:
                        continue

                    # Assumption: If not 4-fold, this suggests
                    # no hollow OR bridge site is present.
                    ovec = ext_surf_coords[edge] - ext_surf_coords[oc]
                    ouvec = ovec / np.linalg.norm(ovec)
                    oangle = np.dot(*ouvec)
                    oright = np.isclose(oangle, 0)
                    if oright:
                        fold4_points.append(potential_hollow)
                        fold4_positions.append(bridge[j])
                else:
                    bridge_points.append(edge)
                    bridge_positions.append(bridge[j])

            if not right.any() and not obtuse.any():
                fold3_position = np.average(ext_surf_coords[corners], axis=0)
                fold3_points += corners.tolist()
                fold3_positions.append(fold3_position)

        fold4_surfaces = ['fcc100','fcc211','fcc311','fcc322','fcc331','bcc100',
                          'bcc210','bcc310','hcp10m10t','hcp10m11','hcp10m12']

        # Complete information of each site
        for n, poss in enumerate([bridge_positions,fold4_positions,fold3_positions]):
            if not poss:
                continue
            fracs = np.stack(poss, axis=0) @ np.linalg.pinv(ref_cell)       
            xfracs, yfracs = fracs[:,0], fracs[:,1]

            # Take only the positions within the periodic boundary
            screen = np.where((xfracs > 0 - 1e-5) & (xfracs < 1 - 1e-5) & \
                              (yfracs > 0 - 1e-5) & (yfracs < 1 - 1e-5))[0]
            reduced_poss = np.asarray(poss)[screen]
            
            # Sort the index list of surface and subsurface atoms 
            # so that we can retrive original indices later
            top2_indices = self.surf_ids + self.subsurf_ids
            top2atoms = self.ref_atoms[top2_indices]

            # Make a new neighborlist including sites as dummy atoms
            dummies = Atoms('X{}'.format(reduced_poss.shape[0]), 
                            positions=reduced_poss, 
                            cell=ref_cell, pbc=self.pbc)
            ntop1, ntop2 = len(self.surf_ids), len(top2atoms)
            testatoms = top2atoms + dummies
            nblist = neighbor_shell_list(testatoms, dx=self.tol, neighbor_number=1, 
                                         different_species=True, mic=True) 
            # Make bridge sites  
            if n == 0:
                fold4_poss = []
                for i, refpos in enumerate(reduced_poss):
                    bridge_indices = nblist[ntop2+i]
                    if not bridge_indices:
                        continue
                    bridgeids = [top2_indices[j] for j in bridge_indices if j < ntop1]
                    if len(bridgeids) != 2: 
                        if self.surface in ['fcc100','fcc211','fcc311','fcc322','fcc331',
                        'bcc100','bcc210','bcc310','hcp10m11','hcp10m12']:
                            fold4_poss.append(refpos)
                            continue
                        else:
                            bridgeids = sorted(bridgeids, key=lambda x: get_mic(        
                                               self.ref_atoms.positions[x], refpos, 
                                               ref_cell, return_squared_distance=True))[:2]
                    si = tuple(sorted(bridgeids))
                    if self.optimize_surrogate_cell:
                        reffrac = refpos @ np.linalg.pinv(ref_cell)
                        pos = (reffrac + np.average(self.delta_positions[bridgeids], 
                               0)) @ self.cell
                    else:
                        pos = refpos + np.average(self.delta_positions[bridgeids], 0) 
                    occurence = np.sum(cm[bridgeids], axis=0)
                    siset = set(si)
                    nstep = len(stepids.intersection(siset))
                    nterrace = len(terraceids.intersection(siset))
                    if self.surface in ['fcc110','hcp10m10h']:
                        this_site = 'bridge'              
                        if nstep == 2:
                            morphology = 'step'
                        elif nstep == 1 and nterrace == 1:
                            morphology = 'sc-tc-h'
                        elif nterrace == 2:                            
                            morphology = 'terrace'
                        else:
                            warnings.warn('Cannot identify site {}'.format(si))
                            assert False
                            continue 
                    elif self.surface in ['fcc311','fcc331']:
                        this_site = 'bridge'
                        if nstep == 2:
                            morphology = 'step'
                        elif nstep == 1 and nterrace == 1:
                            cto2 = list(occurence).count(2)
                            if cto2 == 2:
                                morphology = 'sc-tc-t'
                            elif cto2 == 3:
                                morphology = 'sc-tc-h'
                            else:
                                warnings.warn('Cannot identify site {}'.format(si))
                        elif nterrace == 2:
                            morphology = 'terrace'
                        else:
                            warnings.warn('Cannot identify site {}'.format(si)) 
                            continue          
                    elif self.surface in ['fcc211','fcc322']:             
                        this_site = 'bridge'
                        ncorner = len(cornerids.intersection(siset))
                        if nstep == 2:
                            morphology = 'step'
                        elif nstep == 1 and nterrace == 1:
                            morphology = 'sc-tc-h'
                        elif nstep == 1 and ncorner == 1:
                            morphology = 'sc-cc-t'
                        elif nterrace == 1 and ncorner == 1:
                            morphology = 'tc-cc-h'
                        elif ncorner == 2:
                            morphology = 'corner'
                        # nterrace == 2 is actually terrace bridge, 
                        # but equivalent to tc-cc-h for fcc211
                        elif nterrace == 2:
                            if self.surface == 'fcc211':
                                morphology = 'tc-cc-h'
                            elif self.surface == 'fcc322':
                                morphology = 'terrace'
                        else:
                            warnings.warn('Cannot identify site {}'.format(si)) 
                            continue
                    elif self.surface in ['fcc221','fcc332']:
                        this_site = 'bridge'
                        ncorner = len(cornerids.intersection(siset))
                        if nstep == 2:
                            morphology = 'step'
                        elif nstep == 1 and nterrace == 1:
                            morphology = 'sc-tc-h'
                        elif nstep == 1 and ncorner == 1:
                            morphology = 'sc-cc-h'
                        elif nterrace == 1 and ncorner == 1:
                            morphology = 'tc-cc-h'
                        elif ncorner == 2:
                            morphology = 'corner'
                        elif nterrace == 2:
                            morphology = 'terrace'
                        else:
                            warnings.warn('Cannot identify site {}'.format(si))
                            continue
                    elif self.surface == 'bcc110':
                        this_site, morphology = 'shortbridge', 'terrace'
                    elif self.surface == 'bcc111':
                        ncorner = len(cornerids.intersection(siset))
                        if nstep == 1 and ncorner == 1:
                            this_site, morphology = 'longbridge', 'sc-cc-o'
                        elif nstep == 1 and nterrace == 1:
                            this_site, morphology = 'shortbridge', 'sc-tc-o'
                        elif nterrace == 1 and ncorner == 1:
                            this_site, morphology = 'shortbridge', 'tc-cc-o'
                        elif nstep == 2 or nterrace == 2 or ncorner == 2:
                            continue
                        else:
                            warnings.warn('Cannot identify site {}'.format(si))
                            continue
                    elif self.surface == 'bcc210':            
                        this_site = 'bridge'
                        ncorner = len(cornerids.intersection(siset))
                        if nstep == 2:
                            morphology = 'step'
                        elif nstep == 1 and nterrace == 1:
                            morphology = 'sc-tc-o'
                        elif nstep == 1 and ncorner == 1:
                            morphology = 'sc-cc-t'
                        elif nterrace == 1 and ncorner == 1:
                            morphology = 'tc-cc-o'
                        elif ncorner == 2:
                            morphology = 'corner'
                        # nterrace == 2 is terrace bridge and not 
                        # equivalent to tc-cc-o for bcc210
                        elif nterrace == 2:
                            morphology = 'terrace'
                        else:
                            warnings.warn('Cannot identify site {}'.format(si)) 
                            continue
                    if self.surface == 'bcc211':
                        this_site = 'bridge'
                        if nstep == 2:
                            morphology = 'step'
                        elif nstep == 1 and nterrace == 1:
                            morphology = 'sc-tc-o'
                        elif nterrace == 2:
                            morphology = 'terrace'
                        else:
                            warnings.warn('Cannot identify site {}'.format(si))
                            continue
                    elif self.surface == 'bcc310':
                        this_site = 'bridge'
                        if nstep == 2:
                            morphology = 'step'
                        elif nstep == 1 and nterrace == 1:
                            cto2 = list(occurence).count(2)
                            if cto2 == 2:
                                morphology = 'sc-tc-t'
                            elif cto2 == 3:
                                morphology = 'sc-tc-o'
                            else:
                                warnings.warn('Cannot identify site {}'.format(si))
                        elif nterrace == 2:
                            morphology = 'terrace'
                        else:
                            warnings.warn('Cannot identify site {}'.format(si))
                            continue
                    elif self.surface == 'hcp10m10t':
                        this_site = 'bridge'
                        if nstep == 2:
                            morphology = 'step'
                        elif nstep == 1 and nterrace == 1:
                            morphology = 'sc-tc-t'
                        elif nterrace == 2:
                            morphology = 'terrace'
                        else:
                            warnings.warn('Cannot identify site {}'.format(si))
                            continue
                    elif self.surface == 'hcp10m11':
                        this_site = 'bridge'
                        if nstep == 2:
                            morphology = 'step'
                        elif nstep == 1 and nterrace == 1:
                            cto2 = list(occurence).count(2) 
                            if cto2 == 2:
                                morphology = 'subsurf'
                                isubs = [self.subsurf_ids[i] for i in np.where(
                                         occurence[self.subsurf_ids] == 2)[0]]
                                subpos = self.positions[isubs[0]] + .5 * get_mic(
                                         self.positions[isubs[0]], self.positions[
                                         isubs[1]], self.cell)
                            elif cto2 == 3:
                                morphology = 'sc-tc-h'
                            else:
                                warnings.warn('Cannot identify site {}'.format(si))
                                continue
                        elif nterrace == 2:
                            morphology = 'terrace'
                        else:
                            warnings.warn('Cannot identify site {}'.format(si))
                            continue
                    elif self.surface == 'hcp10m12':
                        this_site = 'bridge'
                        ncorner = len(cornerids.intersection(siset))
                        if nstep == 2:
                            morphology = 'step'
                        elif nstep == 1 and nterrace == 1:
                            morphology = 'sc-tc-h'
                        elif nstep == 1 and ncorner == 1:
                            morphology = 'sc-cc-h'
                        elif nterrace == 1 and ncorner == 1:
                            morphology = 'tc-cc-t'
                        elif ncorner == 2:
                            morphology = 'corner'
                        elif nterrace == 2:
                            morphology = 'terrace'
                        else:
                            warnings.warn('Cannot identify site {}'.format(si))
                            continue
                    elif self.surface in ['fcc111','fcc100','bcc100','hcp0001']:
                        this_site, morphology = 'bridge', 'terrace'
                    
                    site = self.new_site()
                    special = False
                    if self.surface in ['fcc110','bcc211','hcp10m10h'] and morphology == 'terrace':
                        special = True
                        extraids = [xi for xi in np.where(occurence==2)[0]
                                    if xi in self.surf_ids]
                        #if len(extraids) < 2:
                        #    warnings.warn('Cannot identify other 2 atoms of 4-fold site {}'.format(si))
                        if len(extraids) > 2:
                            extraids = sorted(extraids, key=lambda x: get_mic(        
                                       self.ref_atoms.positions[x], refpos, ref_cell,
                                       return_squared_distance=True))[:2]              
                        site.update({'site': this_site,
                                     'surface': self.surface,
                                     'morphology': morphology,
                                     'position': np.round(pos, 8),
                                     'indices': tuple(sorted(bridgeids + extraids))})
                    elif self.surface == 'hcp10m11' and morphology == 'subsurf': 
                        special = True
                        extraids = si
                        site.update({'site': this_site,
                                     'surface': self.surface,
                                     'morphology': morphology,
                                     'position': np.round(subpos, 8),
                                     'indices': tuple(sorted(bridgeids + isubs))})
                    else:                         
                        site.update({'site': this_site,               
                                     'surface': self.surface,
                                     'morphology': morphology,
                                     'position': np.round(pos, 8),
                                     'indices': si})           
                    if self.composition_effect:
                        if self.surface == 'hcp10m11' and morphology == 'subsurf':
                            symbols = [(self.symbols[j], self.numbers[j]) for j in isubs]
                        else:
                            symbols = [(self.symbols[j], self.numbers[j]) for j in si]
                        comp = sorted(symbols, key=lambda x: x[1])
                        composition = ''.join([c[0] for c in comp])
                        if special:
                            extrasymbols = [(self.symbols[xj], self.numbers[xj]) 
                                             for xj in extraids]
                            extra = sorted(extrasymbols, key=lambda x: x[1])
                            extracomp = ''.join([e[0] for e in extra])
                            composition += '-{}'.format(extracomp)
                        site.update({'composition': composition})
                    sl.append(site)
                    usi.add(si)

                if self.surface in fold4_surfaces and fold4_poss:
                    fold4atoms = Atoms('X{}'.format(len(fold4_poss)), 
                                       positions=np.asarray(fold4_poss),
                                       cell=ref_cell, pbc=self.pbc)
                    sorted_top = self.surf_ids
                    ntop = len(sorted_top)
                    topatoms = self.ref_atoms[sorted_top] 
                    newatoms = topatoms + fold4atoms
                    newnblist = neighbor_shell_list(newatoms, dx=.1, 
                                                    neighbor_number=2,
                                                    different_species=True, 
                                                    mic=True) 
                     
                    # Make 4-fold hollow sites
                    for i, refpos in enumerate(fold4_poss):
                        fold4_indices = newnblist[ntop+i]                     
                        fold4ids = [sorted_top[j] for j in fold4_indices]
                        if len(fold4ids) < 4:
                            continue
                        elif len(fold4ids) > 4:
                            fold4ids = sorted(fold4ids, key=lambda x: get_mic(        
                                       self.ref_atoms.positions[x], refpos, ref_cell,
                                       return_squared_distance=True))[:4]
                        occurence = np.sum(cm[fold4ids], axis=0)
                        isub = np.where(occurence >= 4)[0]                        
                        isub = [i for i in isub if i in self.subsurf_ids]
                        if len(isub) == 0:
                            continue
                        isub = isub[0]
                        si = tuple(sorted(fold4ids)) 
                        if self.optimize_surrogate_cell:
                            reffrac = refpos @ np.linalg.pinv(ref_cell)
                            pos = (reffrac + np.average(self.delta_positions[fold4ids], 
                                   0)) @ self.cell
                        else:
                            pos = refpos + np.average(self.delta_positions[fold4ids], 0) 
                        normal = self.get_surface_normal([si[0], si[1], si[2]])
                        for idx in si:
                            normals_for_site[idx].append(normal)

                        site = self.new_site() 
                        if self.surface in ['hcp10m10t','hcp10m11']:
                            this_site = '5fold'
                            site.update({'site': this_site,
                                         'surface': self.surface,
                                         'morphology': 'subsurf',
                                         'position': np.round(self.positions[isub], 8),
                                         'normal': np.round(normal, 8),
                                         'indices': tuple(sorted(fold4ids+[isub]))})
                        else:                                                
                            if self.surface in ['fcc211','fcc322','bcc210']:
                                morphology = 'sc-cc-t'
                            elif self.surface in ['fcc311','fcc331','bcc310']:
                                morphology = 'sc-tc-t'
                            elif self.surface == 'hcp10m12':
                                morphology  = 'tc-cc-t' 
                            else:
                                morphology = 'terrace'

                            this_site = '4fold'
                            site.update({'site': this_site,               
                                         'surface': self.surface,
                                         'morphology': morphology,
                                         'position': np.round(pos, 8),
                                         'normal': np.round(normal, 8),
                                         'indices': si})                     
                        if self.composition_effect:                        
                            metals = self.metals
                            if len(metals) == 1:
                                composition = 4*metals[0]
                            elif len(metals) == 2:
                                ma, mb = metals[0], metals[1]
                                symbols = [self.symbols[i] for i in fold4ids]
                                nma = symbols.count(ma)
                                if nma == 0:
                                    composition = 4*mb
                                elif nma == 1:
                                    composition = ma + 3*mb
                                elif nma == 2:
                                    if this_site == '5fold':
                                        idd = sorted(fold4ids[1:], key=lambda x:        
                                              get_mic(self.positions[x], self.positions[fold4ids[0]],
                                                      self.cell, return_squared_distance=True))
                                        opp, close = idd[-1], idd[0]
                                        if self.symbols[opp] == self.symbols[fold4ids[0]]:
                                            composition = ma + mb + ma + mb 
                                        else:
                                            if self.symbols[close] == self.symbols[fold4ids[0]]:
                                                composition = 2*ma + 2*mb 
                                            else:
                                                composition = ma + 2*mb + ma           
                                    else:
                                        opposite = np.where(cm[si[1:],si[0]]==0)[0]
                                        opp = si[1+opposite[0]]         
                                        if self.symbols[opp] == self.symbols[fold4ids[0]]:
                                            composition = ma + mb + ma + mb 
                                        else:
                                            composition = 2*ma + 2*mb 
                                elif nma == 3:
                                    composition = 3*ma + mb
                                elif nma == 4:
                                    composition = 4*ma
                            else:
                                if this_site == '5fold':
                                    opp = max(list(fold4ids[1:]), key=lambda x:
                                              get_mic(self.positions[x], self.positions[fold4ids[0]],
                                                      self.cell, return_squared_distance=True))
                                    nni = [i for i in fold4ids[1:] if i != opp]
                                    nodes = self.symbols[[fold4ids[0], nni[0], opp, nni[1]]]
                                else:
                                    opposite = np.where(cm[si[1:],si[0]]==0)[0]
                                    opp = si[1+opposite[0]] 
                                    nni = [i for i in si[1:] if i != opp]
                                    nodes = self.symbols[[si[0], nni[0], opp, nni[1]]]
                                composition = ''.join(hash_composition(nodes))
                            site.update({'composition': composition})
                            if this_site == '5fold':                   
                                site['composition'] = '{}-'.format(
                                self.symbols[isub]) + site['composition']
                        if this_site != '5fold':
                            site.update({'subsurf_index': isub})
                            if self.composition_effect:
                                site.update({'subsurf_element': 
                                             self.symbols[isub]})
                        sl.append(site)
                        usi.add(si)
             
            # Make 3-fold hollow sites (differentiate fcc / hcp)
            if n == 2 and self.surface not in ['fcc100','bcc100','hcp10m10t']:
                coexist_3_4 = (self.surface in ['fcc211','fcc311','fcc322','fcc331',
                                                'bcc210','bcc310','hcp10m12'])
                if coexist_3_4:
                    fold4_sites = [s for s in sl if s['site'] == '4fold']

                for i, refpos in enumerate(reduced_poss):
                    fold3_indices = nblist[ntop2+i]
                    fold3ids = [top2_indices[j] for j in fold3_indices if j < ntop1]
                    if len(fold3ids) != 3:
                        #if self.surface != 'hcp10m11':
                        #    si = tuple(sorted(fold3ids))
                        #    warnings.warn('Cannot find the correct atoms of this 3-fold site.',
                        #                  'Find {} instead'.format(si))
                        continue
                    si = tuple(sorted(fold3ids))
                    if self.optimize_surrogate_cell:                                           
                        reffrac = refpos @ np.linalg.pinv(ref_cell)                
                        pos = (reffrac + np.average(self.delta_positions[fold3ids], 
                               0)) @ self.cell
                    else:
                        pos = refpos + np.average(self.delta_positions[fold3ids], 0)

                    # Remove redundant 3-fold sites that belongs to 4-fold sites
                    if coexist_3_4:
                        dup_sites = [s for s in fold4_sites if 
                                     set(fold3ids).issubset(set(s['indices']))]
                        if dup_sites:
                            if any(get_mic(s['position'], pos, self.cell, 
                            return_squared_distance=True) < 1.5 for s in dup_sites):
                                continue
                    normal = self.get_surface_normal([si[0], si[1], si[2]])
                    for idx in si:
                        normals_for_site[idx].append(normal)

                    occurence = np.sum(cm[fold3ids], axis=0)
                    if self.surface in ['fcc211','fcc221','fcc322','fcc332',
                    'hcp10m11','hcp10m12']:
                        if np.max(occurence[self.subsurf_ids]) == 3:
                            this_site = 'hcp'
                        else:
                            this_site = 'fcc'
                        siset = set(si)
                        step_overlap = stepids.intersection(siset)
                        corner_overlap = cornerids.intersection(siset)
                        if step_overlap and not corner_overlap:
                            morphology = 'sc-tc-h'
                        elif corner_overlap and not step_overlap:
                            morphology = 'tc-cc-h'
                        elif step_overlap and corner_overlap:
                            morphology = 'sc-cc-h'    
                        else:
                            morphology = 'terrace'
                    elif self.surface == 'bcc210':
                        this_site = '3fold'
                        siset = set(si)
                        step_overlap = stepids.intersection(siset)
                        corner_overlap = cornerids.intersection(siset)
                        if step_overlap and not corner_overlap:
                            morphology = 'sc-tc-o'
                        elif corner_overlap and not step_overlap:
                            morphology = 'tc-cc-o'
                        else:
                            morphology = 'sc-tc-o'
                    elif self.surface == 'bcc110':
                        this_site, morphology = '3fold', 'terrace'
                    elif self.surface == 'bcc111':
                        this_site, morphology = '3fold', 'sc-tc-cc-o'
                    elif self.surface in ['bcc211','bcc310']:
                        this_site, morphology = '3fold', 'sc-tc-o'
                    elif self.surface in ['fcc111','hcp0001']:
                        morphology = 'terrace'
                        if np.max(occurence[self.subsurf_ids]) == 3:
                            this_site = 'hcp'
                        else:
                            this_site = 'fcc'
                    elif self.surface in ['fcc110','fcc311','fcc331','hcp10m10h']:
                        morphology = 'sc-tc-h'
                        if np.max(occurence[self.subsurf_ids]) == 3:
                            this_site = 'hcp'
                        else:
                            this_site = 'fcc'

                    site = self.new_site()               
                    site.update({'site': this_site,
                                 'surface': self.surface,
                                 'morphology': morphology,
                                 'position': np.round(pos, 8),
                                 'normal': np.round(normal, 8),
                                 'indices': si})
                    if self.composition_effect:                       
                        metals = self.metals                            
                        if len(metals) == 1:
                            composition = 3*metals[0]
                        elif len(metals) == 2:
                            ma, mb = metals[0], metals[1]
                            symbols = [self.symbols[i] for i in si]
                            nma = symbols.count(ma)
                            if nma == 0:
                                composition = 3*mb
                            elif nma == 1:
                                composition = ma + 2*mb
                            elif nma == 2:
                                composition = 2*ma + mb
                            elif nma == 3:
                                composition = 3*ma
                        else:
                            nodes = self.symbols[list(si)]
                            composition = ''.join(hash_composition(nodes))
                        site.update({'composition': composition})   

                    if this_site == 'hcp':
                        isub = np.where(occurence == 3)[0]                        
                        isub = [i for i in isub if i in self.subsurf_ids]
                        if len(isub) == 0:
                            continue
                        isub = isub[0]
                        spos = pos - normal * dh
                        if get_mic(self.positions[isub], spos, self.cell, 
                        return_squared_distance=True) > 2.:
                            site.update({'site': 'fcc'})
                        else:
                            site.update({'subsurf_index': isub}) 
                            if self.composition_effect:
                                site.update({'subsurf_element': 
                                              self.symbols[isub]})
                    sl.append(site)
                    usi.add(si)
 
            if n == 1 and self.surface in fold4_surfaces and list(reduced_poss):
                fold4atoms = Atoms('X{}'.format(len(reduced_poss)), 
                                   positions=np.asarray(reduced_poss),
                                   cell=ref_cell, pbc=self.pbc)
                sorted_top = self.surf_ids
                ntop = len(sorted_top)
                topatoms = self.ref_atoms[sorted_top]
                newatoms = topatoms + fold4atoms
                newnblist = neighbor_shell_list(newatoms, dx=.1, 
                                                neighbor_number=2,
                                                different_species=True, 
                                                mic=True) 

                for i, refpos in enumerate(reduced_poss): 
                    fold4_indices = newnblist[ntop+i]            
                    fold4ids = [sorted_top[j] for j in fold4_indices]
                    if len(fold4ids) < 4:
                        continue
                    elif len(fold4ids) > 4:
                        fold4ids = sorted(fold4ids, key=lambda x: get_mic(        
                                   self.ref_atoms.positions[x], refpos, ref_cell, 
                                   return_squared_distance=True))[:4]             
                    occurence = np.sum(cm[fold4ids], axis=0)
                    isub = np.where(occurence == 4)[0]                    
                    isub = [i for i in isub if i in self.subsurf_ids]
                    if len(isub) == 0:
                        continue
                    isub = isub[0]
                    si = tuple(sorted(fold4ids))
                    if self.optimize_surrogate_cell:
                        reffrac = refpos @ np.linalg.pinv(ref_cell)                
                        pos = (reffrac + np.average(self.delta_positions[fold4ids],
                               0)) @ self.cell
                    else:
                        pos = refpos + np.average(self.delta_positions[fold4ids], 0)
                    normal = self.get_surface_normal([si[0], si[1], si[2]])
                    for idx in si:
                        normals_for_site[idx].append(normal)
                    
                    site = self.new_site()
                    if self.surface in ['hcp10m10t','hcp10m11']:
                        this_site = '5fold'
                        site.update({'site': this_site,
                                     'surface': self.surface,
                                     'morphology': 'subsurf',
                                     'position': np.round(self.positions[isub], 8),
                                     'normal': np.round(normal, 8),
                                     'indices': tuple(sorted(fold4ids+[isub]))})
                    else:
                        if self.surface in ['fcc211','fcc322','bcc210']:
                            morphology = 'sc-cc-t'
                        elif self.surface in ['fcc311','fcc331','bcc310']:
                            morphology = 'sc-tc-t'
                        elif self.surface == 'hcp10m12':
                            morphology  = 'tc-cc-t' 
                        else:
                            morphology = 'terrace'
                        this_site = '4fold'
                        site.update({'site': this_site,
                                     'surface': self.surface,
                                     'morphology': morphology,
                                     'position': np.round(pos, 8),
                                     'normal': np.round(normal, 8),
                                     'indices': si})
                    if self.composition_effect:                       
                        metals = self.metals
                        if len(metals) == 1:
                            composition = 4*metals[0] 
                        elif len(metals) == 2:
                            ma, mb = metals[0], metals[1]
                            symbols = [self.symbols[i] for i in si]
                            nma = symbols.count(ma)
                            if nma == 0:
                                composition = 4*mb
                            elif nma == 1:
                                composition = ma + 3*mb
                            elif nma == 2:
                                if this_site == '5fold':
                                    idd = sorted(fold4ids[1:], key=lambda x:       
                                          get_mic(self.positions[x], self.positions[fold4ids[0]],
                                                  self.cell, return_squared_distance=True))
                                    opp, close = idd[-1], idd[0]
                                    if self.symbols[opp] == self.symbols[fold4ids[0]]:
                                        composition = ma + mb + ma + mb 
                                    else:
                                        if self.symbols[close] == self.symbols[fold4ids[0]]:
                                            composition = 2*ma + 2*mb 
                                        else:
                                            composition = ma + 2*mb + ma  
                                else:
                                    opposite = np.where(cm[si[1:],si[0]]==0)[0]
                                    opp = si[1+opposite[0]]         
                                    if self.symbols[opp] == self.symbols[fold4ids[0]]:
                                        composition = ma + mb + ma + mb 
                                    else:
                                        composition = 2*ma + 2*mb 
                            elif nma == 3:
                                composition = 3*ma + mb
                            elif nma == 4:
                                composition = 4*ma
                        else:
                            if this_site == '5fold':
                                opp = max(list(fold4ids[1:]), key=lambda x:
                                          get_mic(self.positions[x], self.positions[fold4ids[0]],
                                                  self.cell, return_squared_distance=True))
                                nni = [i for i in fold4ids[1:] if i != opp]
                                nodes = self.symbols[[fold4ids[0], nni[0], opp, nni[1]]]
                            else:
                                opposite = np.where(cm[si[1:],si[0]]==0)[0]
                                opp = si[1+opposite[0]] 
                                nni = [i for i in si[1:] if i != opp]
                                nodes = self.symbols[[si[0], nni[0], opp, nni[1]]]
                            composition = ''.join(hash_composition(nodes))
                        site.update({'composition': composition})
                        if this_site == '5fold':
                            site['composition'] = '{}-'.format(
                            self.symbols[isub]) + site['composition'] 
                    if this_site != '5fold':
                        site.update({'subsurf_index': isub})
                        if self.composition_effect:
                            site.update({'subsurf_element': self.symbols[isub]})
                    sl.append(site)
                    usi.add(si)

        if self.surface == 'bcc110':
            bcc110_long_bridges = []
        for t in sl:
            stids = t['indices']
            this_site = t['site']

            # Add normals to ontop sites                                
            if this_site == 'ontop':
                n = np.average(normals_for_site[stids[0]], 0)
                t['normal'] = np.round(n / np.linalg.norm(n), 8)
                nstids = len(stids)
                if nstids > 1:
                    t['site'] = '{}fold'.format(nstids)
                    t['indices'] = tuple(sorted(stids))

            # Add normals to bridge sites
            elif 'bridge' in this_site:
                if t['morphology'] in ['terrace', 'step', 'corner']:
                    normals = []
                    for i in stids[:2]:
                        normals.extend(normals_for_site[i])
                    n = np.average(normals, 0)
                    t['normal'] = np.round(n / np.linalg.norm(n), 8)
                    nstids = len(stids)
                    if nstids > 2:
                        t['site'] = '{}fold'.format(nstids)
                        t['indices'] = tuple(sorted(stids))
                else:
                    if self.surface == 'hcp10m10t':
                        normals = [s['normal'] for s in sl if s['morphology'] 
                                   == 'subsurf' and len(set(s['indices']
                                   ).intersection(set(t['indices']))) == 2]
                    else:
                        # Make sure sc-tc-x and tc-cc-x morphology are the same as x
                        normals = [s['normal'] for s in sl if 
                                   s['morphology'][-1] == t['morphology'][-1] and
                                   'bridge' not in s['site']]
                    t['normal'] = np.round(np.average(normals, 0), 8)
                    nstids = len(stids)
                    if nstids > 2:
                        t['site'] = '{}fold'.format(nstids)
                        t['indices'] = tuple(sorted(stids))
            
            # Take care of longbridge sites on bcc110
            elif self.surface == 'bcc110' and this_site == '3fold':
                si = t['indices']
                pairs = [(si[0], si[1]), (si[0], si[2]), (si[1], si[2])]
                longest = max(pairs, key=lambda x: get_mic(        
                                         self.ref_atoms.positions[x[0]],
                                         self.ref_atoms.positions[x[1]], 
                                         ref_cell, return_squared_distance=True))
                bcc110_long_bridges.append(longest)
        if self.surface == 'bcc110':
            for st in sl:
                if st['site'] == 'shortbridge':
                    if st['indices'] in bcc110_long_bridges:
                        st['site'] = 'longbridge'

        # Add 6-fold sites if allowed
        if self.allow_6fold:            
            for st in sl:
                if self.surface in ['fcc110','hcp10m10h'] and st['site'] == 'bridge' \
                and st['morphology'] == 'step':
                    site = st.copy()                     
                    subpos = st['position'] - st['normal'] * dh / 2
                    sid = list(st['indices'])
                    occurence = cm[sid]
                    surfsi = sid + list(np.where(np.sum(occurence, axis=0) == 2)[0])
                    if len(surfsi) > 4:
                        surfsi = sorted(surfsi, key=lambda x: get_mic(        
                                        self.positions[x], subpos, self.cell,
                                        return_squared_distance=True))[:4]    
                    subsi = [self.subsurf_ids[i] for i in np.where(np.sum(
                             occurence[:,self.subsurf_ids], axis=0) == 1)[0]]
                    if len(subsi) > 2:
                        subsi = sorted(subsi, key=lambda x: get_mic(       
                                       self.positions[x], subpos, self.cell,
                                       return_squared_distance=True))[:2]   
                    si = tuple(sorted(surfsi + subsi))
                    normal = np.asarray([0.,0.,1.])
                    site.update({'site': '6fold',
                                 'position': np.round(subpos, 8),
                                 'morphology': 'subsurf',
                                 'normal': np.round(normal, 8),
                                 'indices': si})
                elif st['site'] == 'fcc':
                    site = st.copy()
                    subpos = st['position'] - st['normal'] * dh / 2                               
                    def get_squared_distance(x):
                        return get_mic(self.positions[x], subpos, 
                                       self.cell, return_squared_distance=True)
                    subsi = sorted(sorted(self.subsurf_ids, 
                                          key=get_squared_distance)[:3])     
                    si = site['indices']
                    site.update({'site': '6fold',      
                                 'position': np.round(subpos, 8),
                                 'morphology': 'subsurf',
                                 'indices': tuple(sorted(si+tuple(subsi)))})
                else:
                    continue
                # Find the opposite element
                if self.composition_effect:
                    metals = self.metals
                    if self.surface in ['fcc110','hcp10m10h']:
                        newsi = surfsi[:-1]
                        subsi.append(surfsi[-1])
                        metals = self.metals 
                        if len(metals) == 1:
                            comp = 3*metals[0]
                        elif len(metals) == 2:
                            ma, mb = metals[0], metals[1]
                            symbols = [self.symbols[i] for i in newsi]
                            nma = symbols.count(ma)
                            if nma == 0:
                                comp = 3*mb
                            elif nma == 1:
                                comp = ma + 2*mb
                            elif nma == 2:
                                comp = 2*ma + mb
                            elif nma == 3:
                                comp = 3*ma
                        else:
                            nodes = self.symbols[list(si)]
                            comp = ''.join(hash_composition(nodes)) 
                    else:
                        comp = site['composition']

                    def get_squared_distance(x):
                        return get_mic(self.positions[x], subpos, 
                                       self.cell, return_squared_distance=True) 
                    if len(metals) == 1:
                        composition = ''.join([comp, 3*metals[0]])
                    elif len(metals) == 2: 
                        ma, mb = metals[0], metals[1]
                        subsyms = [self.symbols[subi] for subi in subsi]
                        nma = subsyms.count(ma)
                        if nma == 0:
                            composition = ''.join([comp, 3*mb])
                        elif nma == 1:
                            ia = subsi[subsyms.index(ma)]
                            subpos = self.positions[ia]
                            if self.symbols[max(si, key=get_squared_distance)] == ma:
                                composition = ''.join([comp, 2*mb + ma])
                            else:
                                composition = ''.join([comp, ma + 2*mb])
                        elif nma == 2:
                            ib = subsi[subsyms.index(mb)]
                            subpos = self.positions[ib]
                            if self.symbols[max(si, key=get_squared_distance)] == mb:
                                composition = ''.join([comp, 2*ma + mb])
                            else:
                                composition = ''.join([comp, mb + 2*ma])
                        elif nma == 3:
                            composition = ''.join([comp, 3*ma])
                    else:                        
                        endsym = re.findall('[A-Z][^A-Z]*', comp)[-1]
                        subpos = [self.positions[i] for i in si if 
                                  self.symbols[i] == endsym][0]
                        nodes = self.symbols[sorted(subsi, key=get_squared_distance)]
                        composition = comp + ''.join(hash_composition(nodes))
                    site.update({'composition': composition})
                sl.append(site)
                usi.add(si)

    def postprocessing(self):
        """Postprocessing the site list, and potentially adding 
        more sites."""

        # Check if the cell is so small that there are sites with duplicate indices             
        small = False
        if not self._allow_expand:
            small = False
        elif self.surface in ['fcc211','fcc311','fcc322','fcc331','bcc210','bcc310','hcp10m12']:
            sorted_sets = sorted([set(s['indices']) for s in self.site_list if s['site'] in 
                                 ['fcc','hcp','3fold','4fold']], key=len, reverse=True)
            for i in range(1, len(sorted_sets)):
                for s, t in zip(sorted_sets, sorted_sets[-i:]):
                    if s.issubset(t):
                        small = True
                        break
                else:
                    continue
                break
        elif len(set(s['indices'] for s in self.site_list)) < len(self.site_list):
            small = True
                                                                                                
        if small:
            self.populate_expanded_site_list()
        else:
            if self.both_sides:
                self.populate_opposite_site_list()
            if self.ignore_bridge_sites:
                self.site_list = [s for s in self.site_list if 'bridge' not in s['site']]
            if self.label_sites:
                self.get_labels()

    def populate_opposite_site_list(self):
        """Collect the sites on the opposite side of the slab."""

        atoms = self.atoms.copy()
        atoms.positions *= [1,1,-1]
        nsas = SlabAdsorptionSites(atoms, surface=self.surface,                                 
                                   allow_6fold=self.allow_6fold,
                                   composition_effect=self.composition_effect, 
                                   both_sides=False,
                                   ignore_bridge_sites=self.ignore_bridge_sites,
                                   label_sites=self.label_sites,
                                   surrogate_metal=self.surrogate_metal,
                                   optimize_surrogate_cell=self.optimize_surrogate_cell,
                                   tol=self.tol, _allow_expand=False)
        # Take only the site positions within the periodic boundary
        bot_site_list = nsas.site_list
        for st in bot_site_list:
            if st['normal'][2] > 0:
                st['normal'] *= [1,1,-1]
            st['position'] *= [1,1,-1]
        self.site_list += bot_site_list
        self.surf_ids += nsas.surf_ids
        self.subsurf_ids += nsas.subsurf_ids

    def populate_expanded_site_list(self):
        """Collect the sites on the 2x2 expanded surface and cell for 
        small unit cells and then return the sites within the original
        unit cell."""

        atoms = self.atoms.copy()
        atoms.wrap()
        atoms *= [2,2,1]
        nsas = SlabAdsorptionSites(atoms, surface=self.surface,                          
                                   allow_6fold=self.allow_6fold,
                                   composition_effect=self.composition_effect, 
                                   both_sides=self.both_sides,
                                   ignore_bridge_sites=self.ignore_bridge_sites,
                                   label_sites=self.label_sites,
                                   surrogate_metal=self.surrogate_metal,
                                   optimize_surrogate_cell=self.optimize_surrogate_cell,
                                   tol=self.tol, _allow_expand=False)
        # Take only the site positions within the periodic boundary
        sl = nsas.site_list
        poss = np.stack([s['position'] for s in sl], axis=0)
        poss = wrap_positions(poss, self.cell, self.pbc)
        D = squareform(pdist(poss))
        screen, wrapped_poss = [], []                             
        seen = set()
        for row, col in zip(*np.where(D < 0.15)):
            if row not in seen:
                screen.append(row)
                wrapped_poss.append(poss[row])
            seen.update([row, col])
        self.site_list = []
        for i, j in enumerate(screen):
            s = sl[j]
            s['position'] = wrapped_poss[i]
            s['indices'] = tuple(sorted(np.mod(s['indices'], len(self.atoms))))
            self.site_list.append(s)

    def get_site(self, indices):
        """Get information of a site given its atom indices.
        
        Parameters
        ----------
        indices : list or tuple
            The indices of the atoms that contribute to the site.
        
        """

        indices = indices if is_list_or_tuple(indices) else [indices]
        indices = tuple(sorted(indices))
        st = next((s for s in self.site_list if 
                   s['indices'] == indices), None)
        return st

    def get_sites(self, site=None,                                                                 
                  morphology=None, 
                  composition=None, 
                  subsurf_element=None):
        """Get information of all sites.
                                                                     
        Parameters                                                   
        ----------                                                   
        site : str, default None
            Only return sites that belongs to this site type.

        morphology : str, default None
            Only return sites with this local surface morphology.

        composition : str, default None
            Only return sites that have this composition.

        subsurf_element : str, default None
            Only return sites that have this subsurface element.
                                                                     
        """                                                          

        all_sites = self.site_list
        if site is not None:
            all_sites = [s for s in all_sites if s['site'] == site] 
        if morphology is not None:
            all_sites = [s for s in all_sites if s['morphology'] == morphology] 
        if composition is not None: 
            if '-' in composition or len(list(Formula(composition))) == 6:
                scomp = composition
            else:
                comp = re.findall('[A-Z][^A-Z]*', composition)
                if len(comp) != 4:
                    scomp = ''.join(sorted(comp, key=lambda x: 
                                           atomic_numbers[x]))
                else:
                    if comp[0] != comp[2]:
                        scomp = ''.join(sorted(comp, key=lambda x: 
                                               atomic_numbers[x]))
                    else:
                        if atomic_numbers[comp[0]] > atomic_numbers[comp[1]]:
                            scomp = comp[1]+comp[0]+comp[3]+comp[2]
                        else:
                            scomp = ''.join(comp)

            all_sites = [s for s in all_sites if s['composition'] == scomp]
        if subsurf_element is not None:
            all_sites = [s for s in all_sites if s['subsurf_element'] 
                         == subsurf_element]

        return all_sites

    def get_unique_sites(self, unique_composition=False,                
                         unique_subsurf=False, 
                         return_signatures=False,
                         return_site_indices=False,
                         site_list=None):
        """Get all symmetry-inequivalent adsorption sites (one
        site for each type).
        
        Parameters
        ----------
        unique_composition : bool, default False
            Take site composition into consideration when 
            checking uniqueness.

        unique_subsurf : bool, default False
            Take subsurface element into consideration when 
            checking uniqueness.

        return_signatures : bool, default False           
            Whether to return the unique signatures of the 
            sites instead.

        return_site_indices: bool, default False
            Whether to return the indices of each unique 
            site (in the site list).                     
        
        """

        if site_list is None:
            sl = self.site_list
        else:
            sl = site_list
        key_list = ['site', 'morphology']
        if unique_composition:
            if not self.composition_effect:
                raise ValueError('the site list does not include '
                                 + 'information of composition')
            key_list.append('composition')
            if unique_subsurf:
                key_list.append('subsurf_element') 
        else:
            if unique_subsurf:
                raise ValueError('to include the subsurface element, ' +
                                 'unique_composition also need to be set to True') 
        if return_signatures:
            sklist = sorted([[s[k] for k in key_list] for s in sl])
            return sorted(list(sklist for sklist, _ in groupby(sklist)))
        else:
            seen_tuple = []
            uni_sites = []
            for i, s in enumerate(sl):
                sig = tuple(s[k] for k in key_list)
                if sig not in seen_tuple:
                    seen_tuple.append(sig)
                    if return_site_indices:
                        s = i
                    uni_sites.append(s)
            return uni_sites                        

    def get_labels(self):
        # Assign labels
        for st in self.site_list:
            if self.composition_effect:
                signature = [st['site'], st['morphology'], st['composition']]                      
            else:
                signature = [st['site'], st['morphology']]
            stlab = self.label_dict['|'.join(signature)]
            st['label'] = stlab                                                        

    def new_site(self):
        return {'site': None, 'surface': None, 'morphology': None, 
                'position': None, 'normal': None, 'indices': None,
                'composition': None, 'subsurf_index': None,
                'subsurf_element': None, 'label': None}

    def mapping(self, atoms):
        """Map the slab into a surrogate reference slab for code versatility."""

        ref_atoms = atoms.copy()
        pm = self.surrogate_metal
        if pm is None:
            common_metal = Counter(self.atoms.symbols).most_common(1)[0][0]
            if common_metal in ['Ni', 'Cu', 'Pd', 'Ag', 'Pt', 'Au']:
                pm = common_metal
        area = np.linalg.norm(np.cross(atoms.cell[0], atoms.cell[1]))
        if self.surface in ['fcc100','fcc110','fcc311','fcc221','fcc331','fcc322',
        'fcc332','bcc210','bcc211']:
            if area < 50.:
                ref_symbol = 'Cu' if pm is None else pm
            else:
                ref_symbol = 'Pt' if pm is None else pm
        elif self.surface in ['fcc111','fcc211','bcc111','hcp0001','hcp10m10h',
        'hcp10m12']:
            ref_symbol = 'Cu' if pm is None else pm
        elif self.surface in ['bcc100','bcc110','bcc310','hcp10m10t','hcp10m11']:
            if area < 50.:
                ref_symbol = 'Cu' if pm is None else pm
            else:
                ref_symbol = 'Au' if pm is None else pm
        else:
            raise ValueError('surface {} is not supported'.format(self.surface))
        for a in ref_atoms:
            a.symbol = ref_symbol
        ref_atoms.calc = asapEMT()

        if self.optimize_surrogate_cell:
            ecf = ExpCellFilter(ref_atoms)
            opt = BFGS(ecf, logfile=None)
        else:
            opt = BFGS(ref_atoms, logfile=None)
        opt.run(fmax=0.1)
        centered_atoms = ref_atoms.copy()
        centered_atoms.center(vacuum=5., axis=2)
        midz = centered_atoms.cell[2][2] / 2
        top_surf_indices = []
        for i, a in enumerate(centered_atoms):
            if abs(a.position[2] - midz) < 3.:
                top_surf_indices = np.asarray([], dtype=int)
                break
            elif a.position[2] > midz:
                top_surf_indices.append(i)
        ref_atoms.positions[top_surf_indices] -= ref_atoms.cell[2]
        ref_atoms.center(vacuum=5., axis=2) 
        ref_atoms.calc = None                      
        if self.optimize_surrogate_cell:
            delta_positions = cart_to_frac(atoms) - cart_to_frac(ref_atoms)
        else:
            delta_positions = atoms.positions - ref_atoms.positions

        return ref_atoms, delta_positions

    def make_neighbor_list(self, neighbor_number=1):
        self.nblist = neighbor_shell_list(self.ref_atoms, self.tol, 
                                          neighbor_number, mic=True)

    def get_connectivity(self):                                      
        """Get the adjacency matrix."""

        return get_adj_matrix(self.nblist)

    def get_termination(self, side='top'):
        """Return the indices of surface and subsurface atoms. This 
        function relies on coordination number and the connectivity 
        of the atoms. The top surface termination is singled out by 
        graph adjacency using networkx.

        Parameters
        ----------
        side : string, default 'top'
            The side of the surface termination ('top' or 'bottom').

        """

        assert side in ['top', 'bottom']
        cm = self.adj_matrix.copy()                               
        np.fill_diagonal(cm, 0)
        indices = self.indices 
        coord = np.count_nonzero(cm, axis=1)
        allsurf = []
        bulk = []
        max_coord = np.max(coord)
        if self.surface == 'bcc210':
            max_coord -= 1

        for i, c in enumerate(coord):
            a_s = indices[i]
            if c >= max_coord:  
                bulk.append(a_s)
            else:
                allsurf.append(a_s)
        surfcm = cm.copy()
        surfcm[bulk] = 0
        surfcm[:,bulk] = 0
        
        # Use networkx to separate top layer and bottom layer
        rows, cols = np.where(surfcm == 1)
        edges = zip(rows.tolist(), cols.tolist())
        G = nx.Graph()
        G.add_edges_from(edges)
        components = nx.connected_components(G)

        if side == 'top':
            surf = list(max(components, 
                        key=lambda x: np.mean(
                        self.ref_atoms.positions[list(x),2])))
        elif side == 'bottom':
            surf = list(min(components,
                        key=lambda x: np.mean(
                        self.ref_atoms.positions[list(x),2])))
        subsurf = []
        for a_b in bulk:
            for a_t in surf:
                if cm[a_t, a_b] > 0:
                    subsurf.append(a_b)
        subsurf = list(np.unique(subsurf))

        return sorted(surf), sorted(subsurf)
 
    def get_two_vectors(self, indices):

        p1 = self.positions[indices[1]]
        p2 = self.positions[indices[2]]
        vec1 = get_mic(p1, self.positions[indices[0]], self.cell)
        vec2 = get_mic(p2, self.positions[indices[0]], self.cell)

        return vec1, vec2

    def get_surface_normal(self, indices):
        """Get the surface normal vector of the plane from the indices 
        of 3 atoms that forms to that plane.                                    
                                                                    
        Parameters
        ----------
        indices : list of tuple
            The indices of the atoms that forms the plane.
        
        """

        vec1, vec2 = self.get_two_vectors(indices)
        n = np.cross(vec1, vec2)
        l = math.sqrt(n @ n.conj())
        n /= l
        if n[2] < 0:
            n *= -1

        return n

    def get_graph(self, return_adj_matrix=False):                              
        """Get the graph representation of the nanoparticle.

        Parameters
        ----------
        return_adj_matrix : bool, default False
            Whether to return adjacency matrix instead of the networkx.Graph 
            object.

        """

        cm = self.adj_matrix
        if return_adj_matrix:
            return cm

        G = nx.Graph()                   
        symbols = self.symbols                               
        G.add_nodes_from([(i, {'symbol': symbols[i]}) 
                          for i in range(len(symbols))])
        rows, cols = np.where(cm == 1)
        edges = zip(rows.tolist(), cols.tolist())
        G.add_edges_from(edges)

        return G

    def get_neighbor_site_list(self, dx=0.1, neighbor_number=1, 
                               radius=None, span=True, unique=False,
                               unique_composition=False,
                               unique_subsurf=False):           
        """Returns the site_list index of all neighbor shell sites 
        for each site.

        Parameters
        ----------
        dx : float, default 0.1
            Buffer to calculate nearest neighbor site pairs.

        neighbor_number : int, default 1
            Neighbor shell number. 

        radius : float, default None
            The radius that defines site a is a neighbor of site b.
            This serves as an alternative to neighbor_number.      

        span : bool, default True
            Whether to include all neighbors sites spanned within 
            the shell.

        unique : bool, default False
            Whether to discard duplicate types of neighbor sites.

        """

        sl = self.site_list
        poss = np.asarray([s['position'] for s in sl])
        statoms = Atoms('X{}'.format(len(sl)), positions=poss,
                        cell=self.cell, pbc=self.pbc)
        if radius is not None:                                                          
            nbslist = neighbor_shell_list(statoms, dx, neighbor_number=1,
                                          mic=True, radius=radius, span=span)
            if unique:
                for i in range(len(nbslist)):
                    nbsids = nbslist[i]
                    tmpids = self.get_unique_sites(unique_composition, unique_subsurf,
                                                   return_site_indices=True,
                                                   site_list=[sl[ni] for ni in nbsids])
                    nbsids = [nbsids[j] for j in tmpids]
                    nbslist[i] = nbsids
        else:
            D = statoms.get_all_distances(mic=True)
            nbslist = {}
            for i, row in enumerate(D):
                argsort = np.argsort(row)
                row = row[argsort]
                res = np.split(argsort, np.where(np.abs(np.diff(row)) > dx)[0] + 1)
                if span:
                    nbsids = sorted([n for nn in range(1, neighbor_number + 1) 
                                     for n in list(res[nn])])
                else:
                    nbsids = sorted(res[neighbor_number])
                if unique:
                    tmpids = self.get_unique_sites(unique_composition, unique_subsurf,
                                                   return_site_indices=True, 
                                                   site_list=[sl[ni] for ni in nbsids])
                    nbsids = [nbsids[j] for j in tmpids]
                nbslist[i] = nbsids

        return nbslist

    def update(self, atoms, update_composition=False):
        """Update the position and composition of each adsorption site 
        given an updated atoms object. Please only use this when the 
        indexing of the atoms object is preserved. Useful for updating
        adsorption sites e.g. after geometry optimization.
        
        Parameters
        ----------
        atoms : ase.Atoms object
            The updated atoms object. 

        update_composition : bool, default False
            Whether to update the composition as well. It is recommended
            to only set update_composition=True if the composition of 
            the surface is not fixed.  

        """

        sl = self.site_list
        new_slab = atoms[[a.index for a in atoms if 
                          a.symbol not in adsorbate_elements]]
        dvecs, _ = find_mic(new_slab.positions - self.positions,
                            self.cell, self.pbc)
        for st in sl:
            si = list(st['indices'])
            st['position'] += np.average(dvecs[si], 0) 
            if update_composition:
                newcomp = ''.join(sorted(atoms.symbols[si], key=
                                         lambda x: atomic_numbers[x]))
                st['composition'] = newcomp                           


def get_adsorption_site(atoms, indices, 
                        surface=None, 
                        return_index=False):
    """A function that returns the information of a site given the
    indices of the atoms that contribute to the site. The function 
    is generalized for both periodic and non-periodic systems
    (distinguished by atoms.pbc).

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    indices : list or tuple
        The indices of the atoms that contribute to the site.

    surface : str, default None
        The surface type (crystal structure + Miller indices)
        Only required for periodic surface slabs.

    return_index : bool, default False
        Whether to return the site index of the site list
        together with the site.

    Example
    -------
    This is an example of getting the site information of the
    (24, 29, 31) 3-fold hollow site on a fcc110 surface:

        >>> from acat.adsorption_sites import get_adsorption_site
        >>> from ase.build import fcc110
        >>> atoms = fcc110('Cu', (2, 2, 8), vacuum=5.)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Au'
        >>> atoms.center()
        >>> site = get_adsorption_site(atoms, (24, 29, 31), surface='fcc110') 
        >>> print(site)

    Output:

    .. code-block:: python

        {'site': 'fcc', 'surface': 'fcc110', 'morphology': 'sc-tc-h', 
         'position': array([ 3.91083333,  1.91449161, 13.5088516 ]), 
         'normal': array([-0.57735027,  0.        ,  0.81649658]), 
         'indices': (24, 29, 31), 'composition': 'CuCuAu', 
         'subsurf_index': None, 'subsurf_element': None, 'label': None}

    """

    indices = indices if is_list_or_tuple(indices) else [indices]                                        
    indices = tuple(sorted(indices))

    if True not in atoms.pbc:
        sas = ClusterAdsorptionSites(atoms, allow_6fold=True,
                                     composition_effect=True)                                                             
    else:
        sas = SlabAdsorptionSites(atoms, surface, 
                                  allow_6fold=True, 
                                  composition_effect=True)             
    site_list = sas.site_list
    sti, site = next(((i, s) for i, s in enumerate(site_list) if                        
                      s['indices'] == indices), None)                     

    if return_index:
        return sti, site
                    
    return site    


def enumerate_adsorption_sites(atoms, surface=None, 
                               morphology=None, **kwargs):
    """A function that enumerates all adsorption sites of the 
    input atoms object. The function is generalized for both 
    periodic and non-periodic systems (distinguished by atoms.pbc).

    Parameters
    ----------
    atoms : ase.Atoms object
        Accept any ase.Atoms object. No need to be built-in.

    surface : str, default None
        The surface type (crystal structure + Miller indices).
        If the structure is a periodic surface slab, this is required.
        If the structure is a nanoparticle, the function enumerates
        only the sites on the specified surface.

    morphology : str, default None
        The function enumerates only the sites of the specified 
        local surface morphology. Only available for surface slabs.

    Example
    -------
    This is an example of enumerating all sites on the fcc100 surfaces
    of a Marks decahedral nanoparticle:

        >>> from acat.adsorption_sites import enumerate_adsorption_sites
        >>> from ase.cluster import Decahedron
        >>> atoms = Decahedron('Pb', p=3, q=2, r=1)
        >>> for atom in atoms:
        ...     if atom.index % 2 == 0:
        ...         atom.symbol = 'Ag'
        >>> atoms.center(vacuum=5.)
        >>> sites = enumerate_adsorption_sites(atoms, surface='fcc100',
        ...                                    composition_effect=True) 
        >>> print(sites[0])

    Output:

    .. code-block:: python

        {'site': '4fold', 'surface': 'fcc100', 
         'position': array([22.63758191, 21.69793997, 13.75044642]), 
         'normal': array([ 0.58778525,  0.80901699, -0.        ]), 
         'indices': (116, 117, 118, 119), 'composition': 'AgAgPbPb', 
         'subsurf_index': 75, 'subsurf_element': 'Pb', 'label': None}

    """

    if True not in atoms.pbc:
        cas = ClusterAdsorptionSites(atoms, **kwargs)
        all_sites = cas.site_list
        if surface is not None:
            all_sites = [s for s in all_sites if 
                         s['surface'] == surface] 

    else:
        sas = SlabAdsorptionSites(atoms, surface, **kwargs)
        all_sites = sas.site_list
        if morphology:
            all_sites = [s for s in all_sites if 
                         s['morphology'] == morphology]       

    return all_sites
