""" A collection of functions to model the electrochemical potential """

__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2018, Karlsruhe Institute of Technology'

import numpy as np
from ase import Atoms
from ase.io import read
from ase.build import add_adsorbate
from ase.constraints import FixAtoms
from ase.constraints import dict2constraint
from data import atoms2dict
from construct import create_structure
from surface import modify_surface_atom
from calculators import classmap
from structure import Structure





def build_structure_generic(params):
    """ construct an atomic structure """
    return atoms2dict(Structure(**params['structure']).atoms)


def build_structure(params):
    """ construct a slab model and add adsorbates """
    # substrate structure
    if params.get('substrate') is not None:
        substr_params = params['substrate']
        if substr_params.get('input structure') is not None:
            # load the structure from params
            substr = substr_params['input structure']
        elif substr_params.get('input file') is not None:
            # read the structure from file
            substr = read(substr_params['input file'])
        else:
            # construct the structure
            substr = create_structure(**substr_params['construct'])

        # constraints
        constraints = None
        if substr_params.get('constrain all atoms'):
            constraints = [FixAtoms(mask=len(substr)*[True])]
        elif substr_params.get('constraints') is not None:
            cparams = substr_params['constraints']
            if isinstance(substr_params['constraints'], list):
                constraints = [dict2constraint(c) for c in cparams]
            else:
                if 'layers' in cparams:
                    cmask = [atom.tag in cparams['layers'] for atom in substr]
                    constraints = [FixAtoms(mask=cmask)]
                else:
                    constraints = [dict2constraint(cparams)]
        if constraints is not None:
            substr.set_constraint(constraints)
            # constr_list = [c.todict() for c in constraints]

        # magmoms
        magmoms = params['substrate'].get('initial magnetic moments')
        if isinstance(magmoms, list):
            substr.set_initial_magnetic_moments(magmoms)
        elif magmoms is not None:
            substr.set_initial_magnetic_moments(len(substr)*[magmoms])

        # modify surface atoms
        if 'modifications' in params['substrate']:
            for mod in params['substrate']['modifications']:
                modify_surface_atom(substr, **mod)

    struct = substr

    # adsorbate structure
    if 'adsorbates' in params and params['adsorbates'] is not None:
        for ads in params['adsorbates']:
            if isinstance(ads['adsorbate'], dict):
                ads['adsorbate'] = Atoms.from_dict(ads['adsorbate'])
            add_adsorbate(struct, **ads)

    struct_dict = atoms2dict(struct)
    return struct_dict


def structure_relaxation(params, struct_dict):
    """ perform structure relaxation with constraints """
    from data import Atoms

    calc_params = params['calculator']['parameters']
    calc_name = str(params['calculator']['name'])
    calc = classmap[calc_name](**calc_params)
    if calc_params.get('restart', False):
        struct = calc.get_atoms()
    else:
        struct = Atoms.from_dict(struct_dict)
        struct.set_calculator(calc)
    calc.calculate(struct)
    assert calc.converged

    struct_dict = atoms2dict(struct)
    energy = struct.get_potential_energy()
    forces = struct.get_forces()
    dipole = struct.get_dipole_moment()
    return struct_dict, energy, forces, dipole

def vibrational_entropy(energies, temperature):
    """ calculate vibrational entropy """
    from ase.units import kB
    beta = 1.0/(kB*temperature)
    entr = 0.0
    for ene in energies:
        exp_hob = np.exp(-ene*beta)
        entr += ene*beta*exp_hob/(1.0-exp_hob)-np.log(1.0-exp_hob)
    entr *= kB
    return entr


def vibrational_partition_function(energies, temperature):
    """ evaluate vibrational partition function """
    from ase.units import kB
    beta = 1.0/(kB*temperature)
    partf = 1
    for ene in energies:
        partf = partf /(1.0-np.exp(-ene*beta))
    return partf


def vibrations(params, struct_dict):
    """ perform normal mode analysis with constraints """

    # optionally extend the list of constraints
    if 'constraints' in params['normal mode analysis']:
        add_constr = params['normal mode analysis']['constraints']
        assert isinstance(add_constr, list)
        if ('constraints' in struct_dict and 
            isinstance(struct_dict['constraints'], list)):
            struct_dict['constraints'].extend(add_constr)
        else:
            struct_dict['constraints'] = add_constr

    struct = Atoms.from_dict(struct_dict)

    # test case of all-atom constraints
    fixatomsc = [c for c in struct.constraints if isinstance(c, FixAtoms)]
    constr = set([idx for c in fixatomsc for idx in c.get_indices()])
    if len(constr) == len(struct):
        return [], 0.0, 0.0, 1.0, 0.0, False, True

    calc_params = params['calculator']['parameters']
    calc_params.update(params['normal mode analysis']['parameters'])
    calc_name = str(params['calculator']['name'])

    calc = classmap[calc_name](**calc_params)
    struct.set_calculator(calc)
    calc.calculate(struct)
    assert calc.converged
    (vib_ene_real, vib_ene_imag) = calc.get_vibrational_energies()

    # calculate properties
    entropy = vibrational_entropy(vib_ene_real, params['temperature'])
    partfun = vibrational_partition_function(vib_ene_real, params['temperature'])
    vet = -params['temperature']*entropy
    zpe = 0.5*np.sum(vib_ene_real)
    tst = len(vib_ene_imag) == 1
    minimum = len(vib_ene_imag) == 0
    return vib_ene_real, entropy, vet, partfun, zpe, tst, minimum


def reaction_energies(props, reactions):
    """ calculate reaction energies """
    for key in props:
        if 'total_entropy_term' not in props[key]:
            props[key]['total_entropy_term'] = (
                props[key]['vibrational_entropy_term'] +
                props[key]['rotational_entropy_term'] +
                props[key]['translational_entropy_term']
            )
    for reac in reactions:
        for term in reac['equation']:
            assert props[term['species']]['energy_minimum']
        for key in ['energy', 'zero_point_energy', 'total_entropy_term']:
            reac[key] = 0.0
            for term in reac['equation']:
                reac[key] += term['coefficient']*props[term['species']][key]
        reac['zpe-corrected energy'] = reac['energy']+reac['zero_point_energy']
        reac['free energy'] = reac['zpe-corrected energy']+reac['total_entropy_term']
    return reactions


def get_ueffumax(reactions):
    """ calculate effective and critical potentials """
    fref = sum(r['free energy'] for r in reactions if r['electrons'] == 0)
    frst = sum(r['free energy'] for r in reactions)
    elec = sum(r['electrons'] for r in reactions)
    u0 = frst/elec
    ueff = u0 - fref/elec
    # sign is positive for cathode reactions
    sign = -np.sign(elec)
    # stopping criterion in case of convergence
    utol = 0.001
    # stopping criterion if umax is in invalid range
    ulim = 10.
    umax = ueff
    delta = ueff / 2.0
    while abs(delta) > utol:
        free_umax = [r['free energy']-r['electrons']*umax for r in reactions]
        if all(feu <= 0 for feu in free_umax):
            if sign*delta < 0:
                delta = -delta / 2.0
        else:
            if sign*delta > 0:
                delta = -delta / 2.0
        umax += delta
        if abs(umax) > ulim:
            umax = -sign*np.infty
            break
    assert sign*ueff > sign*umax
    return ueff, umax


def get_rds(reactions, u0=None):
    """ calculate the rate determining step """
    if u0 is None:
        frst = sum(r['free energy'] for r in reactions)
        elec = sum(r['electrons'] for r in reactions)
        u0 = frst/elec
    free_u0 = [r['free energy']-r['electrons']*u0 for r in reactions]
    rds_ind, rds_free_u0 = max(enumerate(free_u0), key=(lambda x: x[1]))
    return rds_free_u0, print_reaction(reactions[rds_ind])


def print_reaction(reaction):
    """ string representation of a reaction """
    lhs_terms = []
    rhs_terms = []
    for term in reaction['equation']:
        if term['coefficient'] < 0:
            term = str(abs(term['coefficient'])) + ' ' + term['species']
            lhs_terms.append(term)
        else:
            term = str(term['coefficient']) + ' ' + term['species']
            rhs_terms.append(term)
    return ' + '.join(lhs_terms) + ' -> ' + ' + '.join(rhs_terms)


def reverse_reactions(reactions):
    """ return the reverse reactions and their properties """
    result = []
    for r in reversed(reactions):
        react = {}
        for key in r:
            if key == 'equation':
                react['equation'] = []
                for t in reversed(r['equation']):
                    term = {}
                    term['coefficient'] = -t['coefficient']
                    term['species'] = t['species']
                    react['equation'].append(term)
            else:
                react[key] = -r[key]
        result.append(react)
    return result


def potentials_generic(props, reactions, u0=None):
    """ calculate electrochemical potentials and the rate determinig step """

    # calculate the free energies of the specified reactions
    reactions = reaction_energies(props, reactions)

    # effective reversible potential and critical potential
    ueff, umax = get_ueffumax(reactions)

    # rate determinging step at the standard reversible potential u_0
    delta_free_u0, rds = get_rds(reactions, u0)

    return reactions, rds, delta_free_u0, ueff, umax


def potentials(props):
    """ calculate electrochemical potentials for the O2 reduction reaction
        NOTE: deprecated, use potentials_generic() instead """

    u0 = 1.229 # in Volt

    # free energies of species
    free0 = {}
    for spec in ['*', '*o', '*oh', 'o2', 'h2', 'h2o']:
        assert props[spec]['energy_minimum']
        if 'total_entropy_term' in props[spec]:
            total_entropy_term = props[spec]['total_entropy_term']
        else:
            assert 'vibrational entropy term' in props[spec]
            assert 'rotational_entropy_term' in props[spec]
            assert 'translational_entropy_term' in props[spec]
            total_entropy_term = (
                props[spec]['vibrational entropy term'] +
                props[spec]['rotational_entropy_term'] +
                props[spec]['translational_entropy_term']
            )

        free0[spec] = (props[spec]['energy'] +
                       props[spec]['zero_point_energy'] +
                       total_entropy_term)

    # stages: educts and products
    stage1 = '* + 0.5 o2 + h2'
    stage2 = '*o + h2'
    stage3 = '*oh + 0.5 h2'
    stage4 = '* + h2o'

    # number of electrons at each stage
    electrons = {
        stage1: 2,
        stage2: 2,
        stage3: 1,
        stage4: 0
    }

    # free energies of each stage
    free0a = {
        stage1: free0['*'] + 0.5*free0['o2'] + free0['h2'],
        stage2: free0['*o'] + free0['h2'],
        stage3: free0['*oh'] + 0.5*free0['h2'],
        stage4: free0['*'] + free0['h2o']
    }

    # effective reversible potential
    ueff = (free0a[stage2]-free0a[stage4])/(electrons[stage2]-electrons[stage4])
    assert ueff > 0.0

    # critical potential
    tol = 0.001
    umax = ueff
    delta = ueff / 2.0
    while abs(delta) > tol:
        free_umax = {}
        for stage in free0a:
            free_umax[stage] = free0a[stage]-electrons[stage]*umax
        if (free_umax[stage2] >= free_umax[stage3] and
            free_umax[stage3] >= free_umax[stage4]):
            if delta < 0:
                delta = -delta / 2.0
        else:
            if delta > 0:
                delta = -delta / 2.0
        umax += delta

    # rate determinging stage
    free_u0 = {stage: free0a[stage]-electrons[stage]*u0 for stage in free0a}
    delta_free_u0 = {
        stage1+'->'+stage2: free_u0[stage2]-free_u0[stage1],
        stage2+'->'+stage3: free_u0[stage3]-free_u0[stage2],
        stage3+'->'+stage4: free_u0[stage4]-free_u0[stage3],
    }
    rds = max(delta_free_u0, key=delta_free_u0.get)

    return rds, delta_free_u0[rds], ueff, umax


def get_gas_props(props, temperature):
    """ calculate properties of all species: gas species and adsorbates """

    zpe = {
      'h2': 0.270, # eV, J. Phys. Chem. Ref. Data 36, 389 (2007)
      'o2': 0.098, # eV, J. Phys. Chem. Ref. Data 36, 389 (2007)
      'h2o': 0.558 # https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185
    }
    ent = {
      'h2': 1.3613e-3, # https://webbook.nist.gov/cgi/cbook.cgi?ID=C1333740
      'o2': 2.1370e-3, # https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782447
      'h2o': 2.1669e-3 # https://webbook.nist.gov/cgi/cbook.cgi?ID=C7732185
    }
    orr_free = -4.916 # eV, free energy of O2 + 2H2 = 2H2O
    rprops = props
    for spe in rprops:
        if spe in ['h2', 'h2o']:
            rprops[spe]['energy_minimum'] = True
            rprops[spe]['zero_point_energy'] = zpe[spe]
            rprops[spe]['total_entropy_term'] = -temperature*ent[spe]
            rprops[spe]['free energy'] = (rprops[spe]['energy']+
                                          rprops[spe]['zero_point_energy']+
                                          rprops[spe]['total_entropy_term'])
        else:
            if 'total_entropy_term' not in rprops[spe]:
                rprops[spe]['total_entropy_term'] = (
                    rprops[spe]['vibrational entropy term']+
                    rprops[spe]['rotational_entropy_term']+
                    rprops[spe]['translational_entropy_term'])
            rprops[spe]['free energy'] = (rprops[spe]['energy']+
                                          rprops[spe]['zero_point_energy']+
                                          rprops[spe]['total_entropy_term'])
    # special method for o2
    h2o_free = rprops['h2o']['free energy']
    h2_free = rprops['h2']['free energy']
    o2_free = 2*(h2o_free-h2_free)-orr_free
    rprops['o2'] = {}
    rprops['o2']['free energy'] = o2_free
    rprops['o2']['total_entropy_term'] = -temperature*ent['o2']
    rprops['o2']['zero_point_energy'] = zpe['o2']
    rprops['o2']['energy'] = o2_free-(zpe['o2']-temperature*ent['o2'])
    rprops['o2']['energy_minimum'] = True
    return rprops
