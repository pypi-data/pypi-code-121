""" Extend ASE calculators with interoperability methods """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2016, Karlsruhe Institute of Technology'

from ase.units import Hartree

classmap = {}
nsmap = {}
_properties = {}
_parameters = {}

try:
    import ase.calculators.turbomole as turbomole
    from ase.calculators.turbomole import Turbomole
except ImportError:
    raise
else:
    classmap['turbomole'] = Turbomole
    nsmap['Turbomole'] = turbomole

    def get_vibrational_energies():
        """ an interface to return vibrational energies """
        pass
    Turbomole.get_vibrational_energies = get_vibrational_energies

    def get_mos(self):
        """ extracts the molecular orbitals and the orbital energies """
        import numpy as np
        if 'uhf' in self.results['calculation parameters']:
            assert not self.results['calculation parameters']['uhf']
        if 'molecular orbitals' in self.results:
            eigenvectors = []
            eigenvalues = []
            for mo in self.results['molecular orbitals']:
                if mo['spin'] is None:
                    eigenvectors.append(mo['eigenvector'])
                    eigenvalues.append(mo['eigenvalue'])
            return [np.array(eigenvectors),
                    np.diag(np.array(eigenvalues))]
    Turbomole.get_mos = get_mos

    def get_mo(self, mo_type):
        """ returns index and energy of frontier orbitals """
        assert mo_type in ['HOMO', 'LUMO']
        orb_energy = None
        orb_number = None
        if mo_type == 'HOMO':
            for orbital in self.results['molecular orbitals']:
                if orbital['occupancy'] > 0:
                    if orb_energy is None or orbital['eigenvalue'] > orb_energy:
                        orb_energy = orbital['eigenvalue']
                        orb_number = orbital['index']
        if mo_type == 'LUMO':
            for orbital in self.results['molecular orbitals']:
                if orbital['occupancy'] < 1:
                    if orb_energy is None or orbital['eigenvalue'] < orb_energy:
                        orb_energy = orbital['eigenvalue']
                        orb_number = orbital['index']
        return [orb_number, orb_energy]
    Turbomole.get_mo = get_mo

try:
    import ase.calculators.nwchem as nwchem
    from ase.calculators.nwchem import NWChem
except ImportError:
    raise
else:
    classmap.update({'nwchem': NWChem})
    nsmap['NWChem'] = nwchem
    NWChem.converged = True # temporary
    def get_mos(self):
        """ return eigenvectors and eigenvalues as matrices (numpy arrays) """
        import numpy as np
        orbital_coefficients = []
        eigen_energies = []
        for orbital in self.get_property('orbitals'):
            orbital_coefficients.append(orbital['coefficients'])
            eigen_energies.append(orbital['energy'])
        return [
            np.array(orbital_coefficients),
            np.diag(np.array(eigen_energies)*Hartree)
        ]
    NWChem.get_mos = get_mos

    def get_mo(self, mo_type):
        """ returns index and energy of frontier orbitals """
        assert mo_type in ['HOMO', 'LUMO']
        orb_energy = None
        orb_number = None
        if mo_type == 'HOMO':
            for orbital in self.results['orbitals']:
                if orbital['occupation'] > 0:
                    if orb_energy is None or orbital['energy'] > orb_energy:
                        orb_energy = orbital['energy']
                        orb_number = orbital['number']
        if mo_type == 'LUMO':
            for orbital in self.results['orbitals']:
                if orbital['occupation'] < 1:
                    if orb_energy is None or orbital['energy'] < orb_energy:
                        orb_energy = orbital['energy']
                        orb_number = orbital['number']
        return [orb_number, orb_energy*Hartree]
    NWChem.get_mo = get_mo


try:
    from ase.calculators.vasp import Vasp
except ImportError:
    raise
else:
    classmap['vasp'] = Vasp
    _properties['vasp'] = {
        'energy': {'function': 'get_potential_energy', 'args': ['atoms']},
        'forces': {'function': 'get_forces', 'args': ['atoms']},
        'dipole': {'function': 'get_dipole_moment', 'args': ['atoms']},
        'fermi': {'function': 'get_fermi_level', 'args': []},
        'stress': {'function': 'get_stress', 'args': ['atoms']},
        'magmom': {'function': 'get_magnetic_moment', 'args': ['atoms']},
        'magmoms': {'function': 'get_magnetic_moments', 'args': ['atoms']},
        'xc functional': {'function': 'get_xc_functional', 'args': []},
        'eigenvalues': {'function': 'get_eigenvalues', 'args': []},
        'occupation numbers': {'function': 'get_occupation_numbers', 'args': []},
        'number of bands': {'function': 'get_number_of_bands', 'args': []},
        'k-point weights': {'function': 'get_k_point_weights', 'args': []},
        'ibz k-points': {'function': 'get_ibz_kpoints', 'args': []},
        'number of spins': {'function': 'get_number_of_spins', 'args': []},
        'spin polarized': {'function': 'get_spin_polarized', 'args': []},
        'vibrational frequencies': {'function': 'read_vib_freq', 'args': []}
    }
    '''
    _parameters['vasp'] = [
        'float_params',
        'exp_params',
        'string_params',
        'int_params',
        'bool_params',
        'list_params',
        'special_params',
        'dict_params',
        'input_params',
        'name',
        'version',
        'niter',
        'sigma',
        'nelect',
        'converged'
    ]
    '''

    def get_vibrational_energies(self):
        """ an interface to return vibrational energies """
        import numpy as np
        (vib_ene_real, vib_ene_imag) = self.read_vib_freq() # returns in meV
        vib_ene_real = np.array(vib_ene_real)*1.0e-3
        vib_ene_imag = np.array(vib_ene_imag)*1.0e-3
        return vib_ene_real, vib_ene_imag

    Vasp.get_vibrational_energies = get_vibrational_energies


try:
    from ase.calculators.emt import EMT
except ImportError:
    raise
else:
    classmap.update({'emt': EMT})


'''
def calc_get_params(calc):
    """ Return a dictionary with all known parameters """
    params = {}
    for param in _parameters[calc.name]:
        params[param] = getattr(calc, param)
    return params
'''

def calc_get_properties(calc, req_props):
    """ Return a dictionary with properties specified in the list req_props """
    props = {}
    for prop in req_props:
        args = []
        for item in _properties[calc.name][prop]['args']:
            if hasattr(calc, item):
                args.append(getattr(calc, item))
        function = _properties[calc.name][prop]['function']
        props[prop] = getattr(calc, function)(*args)
    return props


def calc_ingest(calc_name, req_props):
    """ Ingest data from a calculation which has not been performed with ASE """
    calc = classmap[calc_name](restart=True)
    assert calc.converged
    atoms = calc.get_atoms()
    props = calc_get_properties(calc, req_props)
    dct = {'calculator': {'name': calc.name, 'parameters': calc.todict()}}
    return (atoms, props, dct)


def calc_dump(calc_name):
    """ Dump data from a calculation which has not been performed with ASE """
    from data import ddump
    calc = classmap[calc_name](restart=True)
    return ddump(calc)


def calculate(atoms, calc_name, calc_parameters):
    """ perform a calculation, return calculator and updated atoms """
    if calc_name == 'nwchem' and 'multiplicity' in calc_parameters:
        calc_parameters['mult'] = calc_parameters['multiplicity']
        del calc_parameters['multiplicity']
    if calc_name == 'nwchem' and 'total charge' in calc_parameters:
        calc_parameters['charge'] = calc_parameters['total charge']
        del calc_parameters['total charge']
    calc = classmap[calc_name](**calc_parameters)
    atoms.set_calculator(calc)
    if calc_name == 'nwchem':
        calc.atoms = atoms
        calc.calculate()
    elif calc_name in ['turbomole', 'vasp']:
        calc.calculate(atoms)
    assert calc.converged
    return calc


def get_energy(atoms, calc_name, calc_parameters):
    """ perform a calculation, return total energy and updated atoms """
    calculate(atoms, calc_name, calc_parameters)
    return atoms.get_total_energy()
