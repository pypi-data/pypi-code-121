""" Functions for modeling charge transport in organic semiconductors for
    sequential workflow execution
"""
__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2016, Karlsruhe Institute of Technology'

from util import atoms2dict
from util import dict2atoms

def prepare_input(parameters):
    """
    input: parameters dict
    output: simulation dict
    """
    from ase.io import read

    title = 'prepare input'
    print('Processing step:', title)

    properties = {}
    simulation = {}
    simulation['morphology'] = {}
    simulation['parameters'] = parameters
    simulation['properties'] = properties

    if 'morphology file' in parameters:
        morphology = read(str(parameters['morphology file']), index=':')
        molecules = []
        for molecule in morphology:
            molecules.append(atoms2dict(molecule, plain_arrays=True))
        simulation['morphology']['molecules'] = molecules
        simulation['monomer structure'] = molecules[0]
    elif 'dimer file' in parameters:
        morphology = read(str(parameters['dimer file']), index=':')
        molecules = []
        for molecule in morphology:
            molecules.append(atoms2dict(molecule, plain_arrays=True))
        simulation['morphology']['molecules'] = molecules
        simulation['optimized monomer structure'] = molecules[0]
    elif 'monomer file' in parameters:
        monomer = read(str(parameters['monomer file']))
        simulation['monomer structure'] = atoms2dict(monomer, plain_arrays=True)
    else:
        raise RuntimeError('morphology / monomer file not found')
    if parameters['carrier'] == 'electron':
        parameters['ion charge'] = parameters['charge']-1
    if parameters['carrier'] == 'hole':
        parameters['ion charge'] = parameters['charge']+1

    return simulation


def optimize_geometry(simulation):
    """
    input: simulation dictionary
    output: simulation dictionary
    """
    from calculators import calculate

    parameters = simulation['parameters']
    monomer = dict2atoms(simulation['monomer structure'], plain_arrays=True)

    title = 'geometry optimization'
    print('Processing step:', title)

    loc_parameters = parameters['calculator']['parameters'].copy()
    loc_parameters['task'] = 'optimize'
    calculate(monomer, parameters['calculator']['name'], loc_parameters)
    simulation['optimized monomer structure'] = atoms2dict(monomer, plain_arrays=True)

    return simulation


def generate_morphology(simulation):
    """
    input: simulation dictionary
    output: simulation dictionary
    """
    from ase import Atoms
    from ase.io import write
    from ase.units import _amu
    from molecules import Morphology
    from morphology import deposit

    monomer = dict2atoms(simulation['monomer structure'], plain_arrays=True)
    parameters = simulation['parameters']

    title = 'generate morphology'
    print('Processing step:', title)

    morphology_type = parameters['morphology type']
    morphology_scale = parameters['morphology scale']
    if morphology_scale == 'atomistic':
        monomer = dict2atoms(
            simulation['optimized monomer structure'],
            plain_arrays=True
        )
    if morphology_type == 'amorphous' and morphology_scale == 'atomistic':
        molecules = deposit(monomer, parameters)
        morphology = Morphology.from_molecules(molecules)
    elif morphology_type == 'crystalline' and morphology_scale == 'coarse-grained':
        if parameters['crystal lattice'] == 'simple cubic':
            morphology = Morphology.SimpleCubic(
                parameters['lattice parameter'],
                parameters['supercell size']
            )
    else:
        raise RuntimeError('unknown morphology type')

    # morphology analysis
    volume = morphology.get_volume()
    mass = morphology.get_mass()
    if mass is not None:
        density_gccm = (mass/volume)*(_amu*1000*1.e24) # 1 cm^3 = 1.e24 Ang^3, _amu in kg
        simulation['properties']['density'] = {'units': 'g/cm^3', 'value': density_gccm}
    [rdf, dist] = morphology.get_rdf(
        parameters['rdf cutoff radius'],
        parameters['rdf number of bins']
    )
    simulation['properties']['rdf'] = [dist.tolist(), rdf.tolist()]

    # plot the RDF
    import matplotlib
    matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend
    import matplotlib.pyplot as plt
    plt.plot(dist, rdf)
    plt.title(parameters['title'])
    plt.xlabel('r, Ang')
    plt.ylabel('g(r)')
    plt.savefig('morphology-rdf.png')

    # visualize morphology
    if morphology_scale == 'atomistic':
        structure = Atoms()
        for molecule in molecules:
            structure += molecule
        write('morphology-structure.xyz', structure)
        write('morphology-structure.png', structure)
        write('morphology-structure.html', structure)
        write('morphology.xyz', molecules)

    # output
    simulation['morphology'] = {}
    if morphology_scale == 'atomistic':
        m_array = []
        for molecule in molecules:
            m_array.append(atoms2dict(molecule, plain_arrays=True))
        simulation['morphology']['molecules'] = m_array
    else:
        simulation['morphology'] = morphology.todict()
    simulation['properties']['number of molecules'] = len(morphology)

    return simulation


def find_pairs(simulation):
    """
    input: simulation dictionary
    output: simulation dictionary
    """
    from transport import get_pairs
    from molecules import Morphology

    parameters = simulation['parameters']
    if 'molecules' in simulation['morphology']:
        molecules = []
        for molecule in simulation['morphology']['molecules']:
            molecules.append(dict2atoms(molecule, plain_arrays=True))
        morphology = Morphology.from_molecules(molecules)
    else:
        morphology = Morphology(**simulation['morphology'])

    title = 'find pairs'
    print('Processing step:', title)
    assert len(morphology) > 1, 'too few or no molecules in morphology'

    [hopping_sites, hopping_pairs] = get_pairs(morphology, parameters['hopping threshold'])
    simulation['hopping sites'] = hopping_sites
    simulation['hopping pairs'] = hopping_pairs

    simulation['properties']['number of hopping sites'] = len(simulation['hopping sites'])
    simulation['properties']['number of hopping pairs'] = len(simulation['hopping pairs'])

    assert len(hopping_sites) > 0, 'no hopping sites found'
    return simulation


def reorganization_energy(simulation):
    """
    input: simulation dictionary
    output: simulation dictionary
    """
    from transport import reorg_energy

    parameters = simulation['parameters']
    molecule = dict2atoms(simulation['optimized monomer structure'], plain_arrays=True)

    title = 'reorganization energy'
    print('Processing step:', title)

    if 'reorganization energy' in parameters:
        lambda_t = parameters['reorganization energy']
        print('reorganization energy read from input')
    else:
        lambda_t = reorg_energy(structure=molecule, parameters=parameters)
    simulation['properties']['reorganization energy'] = {
        'value': lambda_t,
        'units': 'eV'
    }
    return simulation


def site_energies(simulation):
    """
    input: simulation dictionary
    output: simulation dictionary
    """
    import numpy as np
    from calculators import get_energy

    molecules = []
    for molecule in simulation['morphology']['molecules']:
        molecules.append(dict2atoms(molecule, plain_arrays=True))
    parameters = simulation['parameters']
    calc_params = parameters['calculator']['parameters']
    calc_name = parameters['calculator']['name']
    hopping_sites = simulation['hopping sites']

    if len(hopping_sites) < 1:
        raise ValueError('list hopping_sites has zero length')

    title = 'site energies'
    print('Processing step:', title)

    for site in hopping_sites:
        site_atoms = molecules[site['index']]
        site['energy'] = get_energy(site_atoms, calc_name, calc_params)
        if 'electric field' in parameters:
            q = parameters['ion charge']-parameters['charge']
            site['energy'] += -q*np.dot(
                parameters['electric field'],
                site['center of mass']
            )
        calc = site_atoms.get_calculator()
        eigenvectors = calc.get_mos()[0]
        [number, energy] = calc.get_mo('HOMO')
        site['HOMO'] = {
            'energy': energy,
            'number': number,
            'eigenvector': eigenvectors[number-1].tolist()
        }
        [number, energy] = calc.get_mo('LUMO')
        site['LUMO'] = {
            'energy': energy,
            'number': number,
            'eigenvector': eigenvectors[number-1].tolist()
        }

    return simulation


def electronic_couplings(simulation):
    """
    input: simulation dictionary
    output: simulation dictionary
    """
    from transport import get_e_coupling

    morphology = []
    for molecule in simulation['morphology']['molecules']:
        morphology.append(dict2atoms(molecule, plain_arrays=True))
    parameters = simulation['parameters']

    assert len(simulation['hopping pairs']) > 0, 'hopping_pairs has zero length'

    title = 'electronic couplings'
    print('Processing step:', title)
    for pair in simulation['hopping pairs']:
        pair['coupling'] = get_e_coupling(
            left_index=pair['left'],
            right_index=pair['right'],
            parameters=parameters,
            morphology=morphology,
            hopping_sites=simulation['hopping sites'])

    return simulation


def analyses(simulation):
    """
    input: simulation dictionary
    output: simulation dictionary
    """
    from ase import Atoms
    from ase.io import write
    from transport import marcus_rates, mobility

    morphology = []
    for molecule in simulation['morphology']['molecules']:
        morphology.append(dict2atoms(molecule, plain_arrays=True))

    title = 'charge transfer rates'
    print('Processing step:', title)
    marcus_rates(simulation)

    title = 'carrier mobility'
    print('Processing step:', title)
    mobility(simulation)

    # visualization
    import matplotlib
    matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend
    import matplotlib.pyplot as plt
    if 'rdf' in simulation['properties']:
        [dist, rdf] = simulation['properties']['rdf']
        # plot the RDF
        plt.plot(dist, rdf)
        plt.title(simulation['parameters']['title'])
        plt.xlabel('r, Ang')
        plt.ylabel('g(r)')
        plt.savefig('morphology-rdf.png')

    # visualize morphology
    structure = Atoms()
    for molecule in morphology:
        structure += molecule
    write('morphology-structure.xyz', structure)
    write('morphology-structure.png', structure)
    write('morphology-structure.html', structure)
    write('morphology.xyz', morphology)

    return simulation


def graph_analysis(simulation):
    """
    input: simulation dictionary
    output: simulation dictionary
    """
    from molecules import Morphology
    from transport import connected_component_analysis
    from transport import MorphologyGraph

    title = 'graph analysis'
    print('Processing step:', title)

    if 'molecules' in simulation['morphology']:
        molecules = []
        for molecule in simulation['morphology']['molecules']:
            molecules.append(dict2atoms(molecule, plain_arrays=True))
        morphology = Morphology.from_molecules(molecules)
    else:
        morphology = Morphology(
            positions=simulation['morphology']['positions'],
            pbc=simulation['morphology']['pbc'],
            cell=simulation['morphology']['cell']
        )

    cutoff = simulation['parameters']['maxflow cutoff']
    direction = simulation['parameters']['maxflow direction']
    method = simulation['parameters']['maxflow method']
    weights = simulation['parameters']['weights mode']

    results = {}

    if weights == 'couplings':
        results.update(
            connected_component_analysis(
                simulation['morphology'],
                simulation['hopping pairs']
            )
        )

    gr = MorphologyGraph(
        morphology,
        weights=weights,
        hopping_pairs=simulation['hopping pairs'],
        parameters=simulation['parameters']
    )

    ka = gr.get_kirchhoff_index(mode='admittance', normalized=True)
    results['kirchhoff admittance'] = ka

    kr = gr.get_kirchhoff_index(mode='resistance', normalized=True)
    results['kirchhoff resistance'] = kr

    flow = gr.get_total_maxflow(cutoff, direction=direction, method=method, color='blue')
    results['maxflow value'] = flow.value
    results['maxflow cut'] = flow.cut
    results['maxflow flow'] = flow.flow
    results['maxflow partition'] = flow.partition

    simulation['properties'].update(results)

    return simulation
