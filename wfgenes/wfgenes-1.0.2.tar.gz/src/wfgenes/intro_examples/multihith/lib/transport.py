""" functions for modeling charge transport in organic semiconductors """
__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2016, Karlsruhe Institute of Technology'

from math import pi, sqrt, exp
import numpy as np
from ase.units import _hbar, _e, kB
from calculators import calculate, get_energy


def get_pairs(morphology, hopping_threshold):
    """ find pairs of molecules within a cutoff radius (hopping threshold) """
    centers_of_mass = morphology.get_positions()
    hopping_pairs = []
    hopping_sites = []
    hopping_indices = []
    for i in range(len(centers_of_mass)):
        for j in range(i):
            distance_vector = centers_of_mass[i]-centers_of_mass[j]
            distance = np.linalg.norm(distance_vector)
            if distance < hopping_threshold:
                hopping_pairs.append({
                    'distance': distance, 'left': i, 'right': j,
                    'distance vector': distance_vector.tolist()})
                if i not in hopping_indices:
                    hopping_sites.append({'index': i,
                    'center of mass': centers_of_mass[i].tolist()})
                    hopping_indices.append(i)
                if j not in hopping_indices:
                    hopping_sites.append({'index': j,
                    'center of mass': centers_of_mass[j].tolist()})
                    hopping_indices.append(j)
    return [hopping_sites, hopping_pairs]


def get_e_coupling(left_index, right_index, parameters, morphology,
                   hopping_sites):
    """ compute electronic coupling element for two hopping sites """
    assert 'carrier' in parameters, 'carrier type not defined'
    assert parameters['carrier'] in ('electron', 'hole'), (
        'carrier ', parameters['carrier'], ' not supported'
    )
    mo_type = 'HOMO' if parameters['carrier'] == 'hole' else 'LUMO'
    calc_parameters = parameters['calculator']['parameters']

    # structures
    pair = [morphology[left_index], morphology[right_index]]
    dimer = pair[0] + pair[1]

    # dimer
    calc = calculate(dimer, parameters['calculator']['name'], calc_parameters)
    # eigenvectors and eigen energies of the dimer
    [C, e] = calc.get_mos()
    # C^-1
    C_inv = np.linalg.inv(C)
    # overlap matrix and fock matrix: will use FC = SCe
    # overlap matrix of the dimer
    overlap = np.matmul(C_inv, C_inv.T)
    # Fock/Kohn-Sham matrix of the dimer
    fock = np.matmul(C_inv, np.matmul(e, C_inv.T))

    # first monomer
    ar_index = next(
        index for (index, hopping_site) in enumerate(hopping_sites)
        if hopping_site['index'] == left_index
    )
    phi_d_half = np.asarray(hopping_sites[ar_index][mo_type]['eigenvector'])

    # second monomer
    ar_index = next(
        index for (index, hopping_site) in enumerate(hopping_sites)
        if hopping_site['index'] == right_index
    )
    phi_a_half = np.asarray(hopping_sites[ar_index][mo_type]['eigenvector'])

    # electronic coupling J
    # auxiliary zero-valued half-vector
    phi_0_half = np.zeros((np.size(phi_d_half)))
    # donor orbital in the dimer AO basis
    phi_d = np.concatenate((phi_0_half, phi_d_half))
    # acceptor orbital in the dimer AO basis
    phi_a = np.concatenate((phi_a_half, phi_0_half))
    # site energy of donor
    H_dd = np.matmul(np.matmul(phi_d, fock), phi_d)
    # site energy of acceptor
    H_aa = np.matmul(np.matmul(phi_a, fock), phi_a)
    # charge transfer integral between donor and acceptor
    H_da = np.matmul(np.matmul(phi_d, fock), phi_a)
    # overlap between donor and acceptor
    S_da = np.matmul(np.matmul(phi_d, overlap), phi_a)
    # electronic coupling between the two monomers
    e_coupling = (H_da-0.5*(H_aa+H_dd)*S_da)/(1.0-S_da*S_da)

    return e_coupling


def reorg_energy(structure, parameters):
    """ calculate the reorganization energy for the neutral-ion transition """
    loc_parameters = parameters['calculator']['parameters'].copy()
    loc_structure = structure.copy()

    # only doublet charged state supported
    ion_multiplicity = 2
    calc_name = parameters['calculator']['name']

    # relaxation
    loc_parameters['task'] = 'optimize'
    e2_neutral = get_energy(loc_structure, calc_name, loc_parameters)

    # single point energy
    loc_parameters['multiplicity'] = ion_multiplicity
    loc_parameters['total charge'] = parameters['ion charge']
    loc_parameters['task'] = 'energy'
    e1_ion = get_energy(loc_structure, calc_name, loc_parameters)

    # relaxation
    loc_parameters['task'] = 'optimize'
    e2_ion = get_energy(loc_structure, calc_name, loc_parameters)

    # single point energy
    loc_parameters['multiplicity'] = parameters['multiplicity']
    loc_parameters['total charge'] = parameters['charge']
    loc_parameters['task'] = 'energy'
    e1_neutral = get_energy(loc_structure, calc_name, loc_parameters)

    # reorg energy
    return e1_neutral - e2_neutral + e1_ion - e2_ion


def marcus_rates(simulation):
    """ Marcus rates analysis """
    hbar = _hbar / _e
    kBT = kB*simulation['parameters']['temperature']
    lambda_t = simulation['properties']['reorganization energy']['value']
    hopping_sites = simulation['hopping sites']
    if 'positions' in simulation['morphology'].keys():
        morphology_size = len(simulation['morphology']['positions'])
    else:
        morphology_size = len(simulation['morphology']['molecules'])
    A = sqrt(pi/(lambda_t*kBT))/hbar
    B = 1.0/(4.0*lambda_t*kBT)
    energies = morphology_size*[None]
    for site in hopping_sites:
        energies[site['index']] = site['energy']
    for pair in simulation['hopping pairs']:
        deltaE = energies[pair['right']]-energies[pair['left']]
        pair['delta E'] = deltaE
        pair['rate'] = A*pair['coupling']**2*exp(-B*(lambda_t+deltaE)**2)


def abraham_miller_rates():
    pass


def mobility(simulation):
    """ implementation of the GEMM by Rodin et al. PRB 91, 155203 (2015) """
    # parameters
    dimension = 3 # effective spatial dimension of CT (n)
    C = 0.25 # fit parameter, for effective-medium model C=0.25, captures percolation limit
    M = 2 # connectivity parameter, the mean number of site neighbors with J^2 > 0

    energies = np.array([dic['energy'] for dic in simulation['hopping sites']])
    couplings = np.array([dic['coupling'] for dic in simulation['hopping pairs']])
    distances = np.array([dic['distance'] for dic in simulation['hopping pairs']])
    lambda_t = simulation['properties']['reorganization energy']['value']

    e_mean = np.mean(energies)
    sigma = np.std(energies)
    mean_coupling = np.mean((couplings**2)*(distances**2))
    kBT = kB*simulation['parameters']['temperature']
    beta = 1.0/kBT
    beta_sigma = beta*sigma
    beta_lambda = beta*lambda_t
    hbar = _hbar / _e
    mobility_0 = (
        (sqrt(pi)*beta_lambda**1.5)
        /(2.0*dimension*hbar)
        *exp(-beta_lambda/4.0)
        *M*mean_coupling/lambda_t**2
    )
    mobility_1 = (
        mobility_0
        *1.0/sqrt(1.0+beta_sigma**2/beta_lambda)
        *exp(-C*beta_sigma**2)
    )

    props = {}
    props['energy disorder'] = {'value': sigma, 'units': 'eV'}
    props['mean site energy'] = {'value': e_mean, 'units': 'eV'}
    props['mean electronic coupling'] = {'value': mean_coupling, 'units': 'eV^2 Ang^2'}
    props['mobility without energy disorder'] = {'value': mobility_0*1.e-16, 'units': 'cm^2/V.s'}
    props['mobility with energy disorder'] = {'value': mobility_1*1.e-16, 'units': 'cm^2/V.s'}
    simulation['properties'].update(props)

    return


def connected_component_analysis(morphology, hopping_pairs):
    from morphology import gyration_radius

    results = {}

    n_vs = len(morphology['positions'])
    positions = morphology['positions']
    gr = Graph(n_vs)
    gr.vs['label'] = range(n_vs)
    for pair in hopping_pairs:
        gr.add_edge(pair['left'], pair['right'])

    # radius of gyration for the whole morphology
    radius_of_gyration_morphology = gyration_radius(positions)

    rnet_rmor = []  # percolation ratio
    nnet = []       # number of networks
    nconnect = []   # averge number of connections per molecule

    couplings = []
    for pair in hopping_pairs:
        couplings.append(abs(pair['coupling']))
    ects = np.linspace(np.amin(couplings), np.amax(couplings), num=100)
    cinds = np.digitize(couplings, ects)
    cgroups = []
    for eindex, ect in enumerate(ects):
        grp = []
        for ind, cind in enumerate(cinds):
            if cind == eindex:
                pair = hopping_pairs[ind]
                grp.append((pair['left'], pair['right']))
        cgroups.append(grp)

    for eindex, ect in enumerate(ects):
        gr.delete_edges(cgroups[eindex])
        connected_components = gr.clusters()
        cluster_sizes = connected_components.sizes()
        max_cluster = cluster_sizes.index(max(cluster_sizes))
        cluster_vertices = connected_components[max_cluster]
        number_of_networks = len(connected_components)
        nnet.append(number_of_networks)
        # radius of gyration for the largest network
        com = [positions[v] for v in cluster_vertices]
        radius_of_gyration_network = gyration_radius(com)
        rnet_rmor.append(radius_of_gyration_network/radius_of_gyration_morphology)
        # average number of connections per molecule
        nconnect.append(np.sum(gr.degree())/n_vs)

    results['percolation ratio'] = rnet_rmor
    results['number of networks'] = nnet
    results['averge number of connections per molecule'] = nconnect
    results['electronic coupling thresholds'] = ects.tolist()

    return results


from graph import Graph

class MorphologyGraph(Graph):

    directed = False
    weighted = False

    def __init__(self, molecules, weights=None, **kwargs):
        if weights is not None:
            a_key = weights in ['rates', 'couplings', 'distance']
            a_number = isinstance(weights, (float, int))
            if not a_key and not a_number:
                raise ValueError('weights: ' + weights)
            self.hopping_pairs = kwargs['hopping_pairs']
            params = kwargs['parameters']
        if weights == 'rates':
            self.directed = True

        self.molecules = molecules
        self.positions = self.molecules.get_positions()

        Graph.__init__(self, len(self.positions), directed=self.directed)

        self.vs['label'] = range(len(self.positions))
        if weights == None:
            for pair in self.hopping_pairs:
                self.add_edge(pair['left'], pair['right'])
        if weights == 'couplings':
            for pair in self.hopping_pairs:
                self.add_edge(pair['left'], pair['right'], weight=abs(pair['coupling']))
        if weights == 'rates':
            for pair in self.hopping_pairs:
                # use the detailed balance principle
                kBT = kB*params['temperature']
                reverse_rate = pair['rate']*exp(pair['delta E']/kBT)
                self.add_edge(pair['left'], pair['right'], weight=pair['rate'])
                self.add_edge(pair['right'], pair['left'], weight=reverse_rate)
        if type(weights) in [float, int]:
            self.es['weight'] = weights
        if weights == 'distance':
            pass

        self.weighted = self.is_weighted()

    def get_maxflow(self, source, target, color=None):
        mflow = self.maxflow(source, target, capacity="weight")
        if color: mflow.es["color"] = color
        return mflow

    def get_maxflow_value(self, source, target):
        return self.get_maxflow(source, target).value

    def get_maxflow_cut(self, source, target):
        return self.get_maxflow(source, target).cut

    def get_maxflow_flow(self, source, target):
        return self.get_maxflow(source, target).flow

    def plot(self, graph_object, filename='morphgraph.png'):
        from igraph import plot
        plot(graph_object, layout=self.layout('fr'), target=filename)

    def get_total_maxflow(self, cutoff, direction=2, method='superweight',
                          **kwargs):

        self.add_vertex(name='super source', label='S')
        self.add_vertex(name='super target', label='T')
        sindex = next(vertex.index for vertex in self.vs
                      if vertex['name'] == 'super source')
        tindex = next(vertex.index for vertex in self.vs
                      if vertex['name'] == 'super target')

        positions = self.positions

        if method == 'superweight':
            minpos = np.amin(np.array(positions)[:, direction])
            maxpos = np.amax(np.array(positions)[:, direction])
            superweight = 2.0*np.max(self.es['weight'])
            for index, position in enumerate(positions):
                if position[direction] < minpos+cutoff:
                    self.add_edge('super source', index, weight=superweight)
                if position[direction] > maxpos-cutoff:
                    self.add_edge(index, 'super target', weight=superweight)
        if method == 'exponential':
            superweight = np.max(self.es['weight'])
            maxedge = self.es[np.argmax(self.es['weight'])].tuple
            mdistance = self.molecules.get_distance(maxedge[0], maxedge[1])
            print(maxedge, mdistance)
            minpos = np.amin(np.array(positions)[:, direction])-mdistance
            maxpos = np.amin(np.array(positions)[:, direction])+mdistance
            for index, position in enumerate(positions):
                pos = position[direction]
                weight = superweight*np.exp(-(pos-minpos)/cutoff)
                if weight > 1.e-3:
                    self.add_edge('super source', index, weight=weight)
                weight = superweight*np.exp(-(maxpos-pos)/cutoff)
                if weight > 1.e-3:
                    self.add_edge(index, 'super target', weight=weight)
        st_distance = self.shortest_paths(source=sindex, target=tindex)[0][0]
        assert st_distance > 2, ('distance betw. S and T: ' + str(st_distance)
            + '\nS neighbors: ' + str(self.neighbors(sindex))
            + '\nT neighbors: ' + str(self.neighbors(tindex)))
        return self.get_maxflow(sindex, tindex, **kwargs)


    def network_analysis(self, ec_threshold=None, draw_plots=False):
        from morphology import gyration_radius

        results = {}

        if ec_threshold:
            dellist = []
            for pair in self.hopping_pairs:
                if abs(pair['coupling']) < ec_threshold:
                    dellist.append((pair['left'], pair['right']))
            self.delete_edges(dellist)

        connected_components = self.clusters()
        cluster_sizes = connected_components.sizes()
        max_cluster = cluster_sizes.index(max(cluster_sizes))
        cluster_vertices = connected_components[max_cluster]
        number_of_networks = len(connected_components)

        if draw_plots:
            morphology_graph_file = 'morphology-graph.png'
            networks_graph_file = 'networks-graph.png'
            self.plot(filename=morphology_graph_file)
            connected_components.plot(filename=networks_graph_file)
            results['morphology graph file'] = morphology_graph_file
            results['networks graph file'] = networks_graph_file

        # RoG for the largest network
        com = [self.positions[v] for v in cluster_vertices]
        radius_of_gyration_network = gyration_radius(com)
        # RoG for the whole morphology
        radius_of_gyration_morphology = gyration_radius(self.positions)

        results['number of networks'] = number_of_networks
        results['network radius of gyration'] = radius_of_gyration_network
        results['morphology radius of gyration'] = radius_of_gyration_morphology

        return results
