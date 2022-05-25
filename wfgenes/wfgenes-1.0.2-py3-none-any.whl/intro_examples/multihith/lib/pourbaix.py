""" A collection of functions to compute surface Pourbaix diagrams """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2018, Karlsruhe Institute of Technology'

from data import Atoms
from data import atoms2dict
from data import single_entry
from calculators import classmap

def structure_relaxation(structure, test=False):
    """ perform structure relaxation """

    structure = single_entry(structure)
    if test:
        return {
            'atoms': structure['atoms'],
            'properties': {
               'energy': 0.0,
               'forces': None,
               'dipole': None
            },
            'parameters': structure['parameters']
        }

    atoms = Atoms.from_dict(structure['atoms'])
    params = structure['parameters']
    calc_params = params['calculator']['parameters']
    calc_name = str(params['calculator']['name'])
    if 'ropt' in calc_params:
        ropt = calc_params['ropt']
        if not isinstance(ropt, list):
            calc_params['ropt'] = len(set(atoms.get_atomic_numbers()))*[ropt]
    calc = classmap[calc_name](**calc_params)
    atoms.set_calculator(calc)
    calc.calculate(atoms)
    assert calc.converged

    adict = atoms2dict(atoms)
    energy = adict.pop('energy')
    forces = adict.pop('forces')
    dipole = adict.pop('dipole')
    return {
        'atoms': adict,
        'properties': {
           'energy': energy,
           'forces': forces,
           'dipole': dipole
        },
        'parameters': params
    }

def free_energy(entry, ads_props):
    """ approximated free energy using average values for ZPE and entropy """
    entry = single_entry(entry)
    zpe = 0.0
    vet = 0.0
    for ads in entry['parameters']['adsorbates']:
        atoms = Atoms.from_dict(ads['adsorbate'])
        adskey = atoms.get_chemical_formula(mode='hill').lower()
        zpe += ads_props[adskey]['zero-point energy']
        vet += ads_props[adskey]['vibrational entropy term']
    entry['properties']['free energy'] = entry['properties']['energy'] + zpe + vet
    entry['properties']['zero-point energy'] = zpe
    entry['properties']['total entropy term'] = vet
    # assuming energy minimum
    entry['properties']['energy minimum'] = True
    return entry

def substrate_entry(entries):
    """ detect and select the substrate entry """
    substr_entry = [e for e in entries if len(e['parameters']['adsorbates'])==0]
    try:
        entry = single_entry(substr_entry)
    except AssertionError:
        if len(substr_entry) == 0:
            print('substrate entry not found')
        if len(substr_entry) > 1:
            print('several substrate entries found')
        raise

    entry['properties']['free energy'] = entry['properties']['energy']
    entry['properties']['zero-point energy'] = 0.000
    entry['properties']['total entropy term'] = 0.000
    entry['properties']['energy minimum'] = True
    return entry

def formation_energy(entry, substrate, gas_entries):
    """ calculate formation energy of the complex from elemental species """
    from ueffumax import reaction_energies
    from data import Atoms

    entry = single_entry(entry)
    props = {}
    props['complex'] = entry['properties']
    props['substrate'] = substrate['properties']
    props.update(gas_entries)

    atoms = Atoms.from_dict(entry['atoms'])
    nhydr = len([s for s in atoms.get_chemical_symbols() if s == 'H'])
    noxyg = len([s for s in atoms.get_chemical_symbols() if s == 'O'])
    reactions = [{
      'equation': [
        {'species': 'substrate', 'coefficient': -1.},
        {'species': 'h2', 'coefficient': -nhydr/2.},
        {'species': 'o2', 'coefficient': -noxyg/2.},
        {'species': 'complex', 'coefficient': 1.}
      ]
    }]
    reactions = reaction_energies(props, reactions)
    entry['properties']['reactions'] = reactions
    keylist = ['energy', 'zero-point energy', 'zpe-corrected energy',
               'total entropy term', 'free energy']
    for key in keylist:
        entry['properties'][key] = reactions[0][key]
    return entry

def pourbaix_diagram(ion_entries, comp_entries):
    """ construct a surface Pourbaix diagram """
    from pymatgen.entries.computed_entries import ComputedEntry
    from pymatgen.analysis.pourbaix_diagram import PourbaixEntry
    from pymatgen.analysis.pourbaix_diagram import PourbaixDiagram
    from pymatgen.analysis.pourbaix_diagram import PourbaixPlotter

    if all(isinstance(e, PourbaixEntry) for e in ion_entries):
        entries = ion_entries
    else:
        entries = [PourbaixEntry.from_dict(edict) for edict in ion_entries]
    for entry in comp_entries:
        atoms = Atoms.from_dict(entry['atoms'])
        composition = atoms.get_chemical_formula(mode='hill')
        energy = entry['properties']['free energy']
        entries.append(PourbaixEntry(ComputedEntry(composition, energy)))
    pbx = PourbaixDiagram(entries)
    plotter = PourbaixPlotter(pbx)
    plot = plotter.get_pourbaix_plot()
    plot.savefig('fig.png')
