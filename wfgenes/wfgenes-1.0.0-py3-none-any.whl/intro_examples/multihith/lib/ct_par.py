""" Functions for modeling charge transport in organic semiconductors for
    parallel workflow execution
"""
__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2016, Karlsruhe Institute of Technology'


def prepare_input(parameters):
    """
    input: parameters file
    output: parameters, monomer_structure
    """
    from ase.io import read
    from util import atoms2dict

    title = 'prepare input'
    print('Processing step:', title)

    monomer = read(str(parameters['monomer file']))
    monomer_structure = atoms2dict(monomer, plain_arrays=True)

    return monomer_structure, parameters


def optimize_geometry(monomer_structure, parameters):
    """
    node input: monomer structure, parameters
    node output: optimized monomer structure
    """
    from util import dict2atoms, atoms2dict
    from calculators import calculate

    monomer = dict2atoms(monomer_structure, plain_arrays=True)

    title = 'geometry optimization'
    print('Processing step:', title)

    loc_parameters = parameters['calculator']['parameters'].copy()
    loc_parameters['task'] = 'optimize'
    calculate(monomer, parameters['calculator']['name'], loc_parameters)
    return atoms2dict(monomer, plain_arrays=True)


def reorganization_energy(monomer_structure, parameters):
    """
    node input: monomer structure, parameters (ro)
    node output: reorganization_energy
    """
    from util import dict2atoms
    from transport import reorg_energy

#    molecule = dict2atoms(monomer_structure, plain_arrays=True)
#    properties = {}

    title = 'reorganization energy'
    print('Processing step:', title)

    if parameters['carrier'] == 'electron':
        parameters['ion charge'] = parameters['charge']-1
    if parameters['carrier'] == 'hole':
        parameters['ion charge'] = parameters['charge']+1

    if 'reorganization energy' in parameters:
        lambda_t = parameters['reorganization energy']
        print('reorganization energy read from input')
    else:
        lambda_t = reorg_energy(
            structure=dict2atoms(monomer_structure, plain_arrays=True),
            parameters=parameters
        )
#    properties['reorganization energy'] = {'value': lambda_t, 'units': 'eV'}
#    return properties['reorganization energy']
    return {'value': lambda_t, 'units': 'eV'}


def generate_morphology(monomer_structure, parameters, properties):
    """
    input: monomer structure, parameters
    output: morphology, properties
    """
    import matplotlib
    matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend
    import matplotlib.pyplot as plt
    from ase import Atoms
    from ase.io import write
    from ase.units import _amu
    from util import dict2atoms, atoms2dict
    from molecules import Morphology
    from morphology import deposit

    monomer = dict2atoms(monomer_structure, plain_arrays=True)

    title = 'generate morphology'
    print('Processing step:', title)
    morphology_type = parameters['morphology type']
    morphology_scale = parameters['morphology scale']
    if morphology_scale == 'atomistic':
        monomer = dict2atoms(monomer_structure, plain_arrays=True)
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
        properties['density'] = {'units': 'g/cm^3', 'value': density_gccm}
    [rdf, dist] = morphology.get_rdf(
        parameters['rdf cutoff radius'],
        parameters['rdf number of bins']
    )
    properties['rdf'] = [dist.tolist(), rdf.tolist()]

    # plot the RDF
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

    # output
    morphology_dct = morphology.todict()
    if morphology_scale == 'atomistic':
        m_array = []
        for molecule in molecules:
            m_array.append(atoms2dict(molecule, plain_arrays=True))
        morphology_dct['molecules'] = m_array
    properties['number of molecules'] = len(morphology)

    return morphology_dct, properties


def find_pairs(morphology, parameters):
    """
    input: morphology, parameters
    output: hopping sites, hopping pairs
    """
    from util import dict2atoms
    from molecules import Morphology
    from transport import get_pairs

    if 'molecules' in morphology:
        molecules = []
        for molecule in morphology['molecules']:
            molecules.append(dict2atoms(molecule, plain_arrays=True))
        morphology = Morphology.from_molecules(molecules)
    else:
        morphology = Morphology(**morphology)

    assert len(morphology) > 1, 'too few or no molecules in morphology'

    title = 'find pairs'
    print('Processing step:', title)

    [hopping_sites, hopping_pairs] = get_pairs(morphology, parameters['hopping threshold'])

    assert len(hopping_sites) > 0, 'no hopping sites found'

    return hopping_sites, hopping_pairs


def site_energies(hopping_sites, morphology, parameters):
    """
    input: hopping sites, morphology, parameters
    output: hopping sites
    """
    import numpy as np
    from util import dict2atoms
    from calculators import get_energy

    title = 'site energies'
    print('Processing step:', title)

    molecules = []
    for molecule in morphology['molecules']:
        molecules.append(dict2atoms(molecule, plain_arrays=True))

    assert len(hopping_sites) > 0, 'list hopping_sites has zero length'

    if parameters['carrier'] == 'electron':
        parameters['ion charge'] = parameters['charge']-1
    if parameters['carrier'] == 'hole':
        parameters['ion charge'] = parameters['charge']+1

    if not isinstance(hopping_sites, list):
        singletask = True
        hopping_sites = [hopping_sites]
    else:
        singletask = False

    calc_params = parameters['calculator']['parameters']
    calc_name = parameters['calculator']['name']
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

    if singletask:
        return hopping_sites[0]
    else:
        return hopping_sites


def electronic_couplings(hopping_pairs, hopping_sites, morphology, parameters):
    """
    input: hopping pairs
    output: hopping pairs
    """
    from util import dict2atoms
    from transport import get_e_coupling

    molecules = []
    for molecule in morphology['molecules']:
        molecules.append(dict2atoms(molecule, plain_arrays=True))

    assert len(hopping_pairs) > 0, 'list hopping_pairs has zero length'

    title = 'electronic couplings'
    print('Processing step:', title)

    if not isinstance(hopping_pairs, list):
        singletask = True
        hopping_pairs = [hopping_pairs]
    else:
        singletask = False

    for pair in hopping_pairs:
        pair['coupling'] = get_e_coupling(
            left_index=pair['left'],
            right_index=pair['right'],
            parameters=parameters,
            morphology=molecules,
            hopping_sites=hopping_sites)

    if singletask:
        return hopping_pairs[0]
    else:
        return hopping_pairs


def analyses(simulation):
    """
    input: hopping sites, hopping pairs
    output: [deltaE, rate] for each hopping pair, sigma, mean_coupling, mobility
    parameters (as constants): n, C, M
    """
    from util import dict2atoms
    from ase import Atoms
    from ase.io import write
    from transport import marcus_rates, mobility
    import matplotlib
    matplotlib.use('Agg') # Force matplotlib to not use any Xwindows backend
    import matplotlib.pyplot as plt

    simulation['properties']['reorganization energy'] = simulation['reorganization energy']
    del simulation['reorganization energy']

    title = 'charge transfer rates'
    print('Processing step:', title)
    marcus_rates(simulation)

    title = 'carrier mobility'
    print('Processing step:', title)
    mobility(simulation)

    # visualization
    if 'rdf' in simulation['properties']:
        [dist, rdf] = simulation['properties']['rdf']
        plt.plot(dist, rdf)
        plt.title(simulation['parameters']['title'])
        plt.xlabel('r, Ang')
        plt.ylabel('g(r)')
        plt.savefig('morphology-rdf.png')

    # visualize morphology
    molecules = []
    for molecule in simulation['morphology']['molecules']:
        molecules.append(dict2atoms(molecule, plain_arrays=True))
    structure = Atoms()
    for molecule in molecules:
        structure += molecule
    write('morphology-structure.xyz', structure)
    write('morphology-structure.png', structure)
    write('morphology-structure.html', structure)
    write('morphology.xyz', molecules)

    return simulation
