"""Comparator objects based on graph theory."""
from ..adsorbate_coverage import ClusterAdsorbateCoverage
from ..adsorbate_coverage import SlabAdsorbateCoverage
from ..utilities import neighbor_shell_list, get_adj_matrix
from ase.atoms import Atoms
import networkx as nx
import numpy as np


class AdsorptionGraphComparator(object):
    """Compares the graph of adsorbate overlayer + surface atoms and 
    returns True if they are isomorphic with node matches. Before checking 
    graph isomorphism by color refinement, a cheap label match is used to 
    reject graphs that are impossible to be isomorphic.

    The graphs (nx.Graph objects) can be quite costly to obtain every time 
    a graph is required (and disk intensive if saved), thus it makes sense 
    to get the graph along with e.g. the potential energy and save it in 
    atoms.info['data']['graph'].

    Parameters
    ----------
    adsorption_sites : acat.adsorption_sites.ClusterAdsorptionSites object \
        or acat.adsorption_sites.SlabAdsorptionSites object
        Provide the acat built-in adsorption sites class to accelerate the 
        pattern generation. Make sure all the structures have the same 
        atom indexing. 

    composition_effect : bool, default True
        Whether to consider sites with different elemental compositions as 
        different sites. It is recommended to set composition_effet=False 
        for monometallics.

    subtract_height : bool, default False
        Whether to subtract the height from the bond length when allocating
        a site to an adsorbate. Default is to allocate the site that is
        closest to the adsorbate's binding atom without subtracting height.
        Useful for ensuring the allocated site for each adsorbate is
        consistent with the site to which the adsorbate was added. 

    hmax : int, default 2
        Maximum number of iterations for color refinement.

    dmax : float, default 2.5
        The maximum bond length (in Angstrom) between an atom and its
        nearest site to be considered as the atom being bound to the site.

    """

    def __init__(self, adsorption_sites,  
                 composition_effect=True,
                 subtract_height=False,
                 hmax=2, dmax=2.5, **kwargs):
        
        self.adsorption_sites = adsorption_sites
        self.composition_effect = composition_effect
        self.subtract_height = subtract_height
        self.hmax = hmax
        self.dmax = dmax
        self.kwargs = kwargs
        self.comp = WLGraphComparator(hmax=self.hmax)

    def looks_like(self, a1, a2):
        isocheck = False
        if ('data' in a1.info and 'graph' in a1.info['data']) and (
        'data' in a2.info and 'graph' in a2.info['data']):
            isocheck = True
            G1 = a1.info['data']['graph']
            G2 = a2.info['data']['graph']
        else:
            sas = self.adsorption_sites        
 
            if hasattr(sas, 'surface'):
                sas.update(a1, update_composition=self.composition_effect)
                sac1 = SlabAdsorbateCoverage(a1, sas, subtract_height=
                                             self.subtract_height, 
                                             label_occupied_sites=True, 
                                             dmax=self.dmax)
                sas.update(a2, update_composition=self.composition_effect)
                sac2 = SlabAdsorbateCoverage(a2, sas, subtract_height=
                                             self.subtract_height, 
                                             label_occupied_sites=True, 
                                             dmax=self.dmax)
            else:
                sas.update(a1, update_composition=self.composition_effect)
                sac1 = ClusterAdsorbateCoverage(a1, sas, subtract_height=
                                                self.subtract_height, 
                                                label_occupied_sites=True,
                                                dmax=self.dmax)
                sas.update(a2, update_composition=self.composition_effect)
                sac2 = ClusterAdsorbateCoverage(a2, sas, subtract_height=
                                                self.subtract_height, 
                                                label_occupied_sites=True,
                                                dmax=self.dmax)
            labs1 = sac1.get_occupied_labels(fragmentation=self.kwargs.get(
                                             'fragmentation', True))
            labs2 = sac2.get_occupied_labels(fragmentation=self.kwargs.get(
                                             'fragmentation', True))       
 
            if labs1 == labs2:
                isocheck = True 
                G1 = sac1.get_graph(self.kwargs)
                G2 = sac2.get_graph(self.kwargs)
        if isocheck:
            if self.comp.looks_like(G1, G2):
                return True

        return False


class WLGraphComparator(object):
    """Compares two structures (or graphs) based on the Weisfeiler-Lehman 
    subtree kernel (color refinement), as described in N. Shervashidze et 
    al., Journal of Machine Learning Research 2011, 12, 2539–2561. This 
    serves as a scalable solver for checking graph isomorphism of two 
    structures. 

    The graphs (nx.Graph objects) can be quite costly to obtain every time 
    a graph is required (and disk intensive if saved), thus it makes sense 
    to get the graph along with e.g. the potential energy and save it in 
    atoms.info['data']['graph'].

    Parameters
    ----------
    hmax : int, default 2
        Maximum number of iterations for color refinement.

    dx : float, default 0.5
        Buffer to calculate nearest neighbor pairs.

    tol : float, default 1e-5
        Tolerance of the discrepancy between K12 and sqrt(K11*K22)

    """

    def __init__(self, hmax=2, dx=.5, tol=1e-5):
        self.hmax = hmax
        self.dx = dx
        self.tol = tol

    def looks_like(self, a1, a2):
        if isinstance(a1, Atoms) and isinstance(a2, Atoms):
            if ('data' in a1.info and 'graph' in a1.info['data']) and (
            'data' in a2.info and 'graph' in a2.info['data']):
                a1 = a1.info['data']['graph']
                a2 = a2.info['data']['graph']
        d1 = WLGraphComparator.get_label_dict(a1, self.hmax, self.dx)
        d2 = WLGraphComparator.get_label_dict(a2, self.hmax, self.dx)
        d12 = {k: [d[k] if k in d else 0 for d in (d1, d2)] 
               for k in set(d1.keys()) | set(d2.keys())}
        X12 = np.asarray(list(d12.values()))

        # Compute the inner products
        k11 = sum(v**2 for v in d1.values())
        k22 = sum(v**2 for v in d2.values())
        k12 = X12[:,0] @ X12[:,1].T

        return abs(k12 - (k11 * k22)**0.5) <= self.tol 

    @classmethod
    def get_label_dict(cls, G, hmax, dx):                                                        
        d = {}
        if isinstance(G, Atoms):
            atoms = G.copy()
            symbols = atoms.symbols
            nblist = neighbor_shell_list(atoms, dx=dx, neighbor_number=1, 
                                         mic=(True in atoms.pbc))                     
            A = get_adj_matrix(nblist)
            N = len(A)
            G = nx.from_numpy_matrix(A)
        else:
            N = G.number_of_nodes()
            symbols = np.asarray([G.nodes[i]['symbol'] for i in range(N)], 
                                 dtype=object)

        nnlabs, neighbors = {}, {}
        isolates = []
        for i in range(N):
            lab0 = str(symbols[i])
            if lab0 in d:
                d[lab0] += 1.
            else:
                d[lab0] = 1.
            if hmax > 0:
                nnd = nx.single_source_shortest_path_length(G, i, cutoff=1)
                nns = [j for j, v in nnd.items() if v == 1]
                neighbors[i] = nns
                if len(nns) == 0:
                    isolates.append(i)
                    continue
                sorted_symbols = sorted(symbols[nns])
                lab1 = lab0 + ':' + ','.join(sorted_symbols)
                nnlabs[i] = lab1
                if lab1 in d:
                    d[lab1] += 1 
                else:
                    d[lab1] = 1
        if hmax > 1: 
            for k in range(1, hmax):
                nnnlabs = {}
                for i in range(N):
                    if i in isolates:
                        continue
                    nnlab = nnlabs[i]
                    nnnlab = ','.join(sorted(nnlabs[nn] for nn in neighbors[i]))
                    lab = nnlab + ':' * (k + 1) + nnnlab
                    nnnlabs[i] = lab
                    if lab in d:
                        d[lab] += 1
                    else:
                        d[lab] = 1
                nnlabs = nnnlabs 

        return d
