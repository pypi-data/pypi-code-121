""" functions for constructing, manipulating and analyzing morphologies """
__author__ = 'Ivan Kondov'
__email__ = 'ivan.kondov@kit.edu'
__copyright__ = 'Copyright 2016, Karlsruhe Institute of Technology'


import random as rnd
import numpy as np
from ase import Atoms
from ase.data.vdw import vdw_radii
from ase.geometry import find_mic


def vdw_clash(morphology, num):
    """ Test whether a molecule (particle) is clashing with some of the rest """
    cutoffs = [vdw_radii[number] for number in morphology.get_atomic_numbers()]
    mol_new_ind = range(len(morphology)-num, len(morphology))
    rest_ind = range(0, len(morphology)-num)
    for index1 in mol_new_ind:
        distances = morphology.get_distances(index1, rest_ind, mic=True)
        for index2, distance in enumerate(distances):
            if distance < cutoffs[index1]+cutoffs[index2]:
                return True
    return False


def rmsd(reference, structure):
    """ Calculates the Root Mean Square Deviation between a structure
    and a reference both provided as Atoms objects """
    from ase.build import minimize_rotation_and_translation
    var_structure = Atoms(structure)
    minimize_rotation_and_translation(reference, var_structure)
    return np.sqrt(
        np.mean(
            (np.linalg.norm(var_structure.get_positions()
                            -reference.get_positions(), axis=1))**2, axis=0
        )
    )


def deposit(mol, parameters):
    """ Deposition of molecules of one type in a box. The molecules get random
    positions and orientations and clashing molecules are removed """
    clash_distance = parameters['clash distance']
    trials = parameters['trials']
    seed = parameters['rng seed']
    a = parameters['cell size']
    thkz = 1.0
    varz = True

    mol.set_cell([a, a, a])
    mol.set_pbc((1, 1, 1))
    pbc = mol.get_pbc()
    cell = mol.get_cell()
    natoms = len(mol)
    if varz:
        depz = 0.0
        mol.center(about=([a/2, a/2, 0.]))
    else:
        depz = thkz
        mol.center(about=([a/2, a/2, a/2]))

    inserted = 1
    clashed = 0
    depz_step = thkz/trials

    morphology_list = [mol.copy()]
    morphology_stack = mol.copy()

    rnd.seed(seed)

    trial = 0
    while trial < trials:
        trial += 1
        mol_new = mol.copy()
        if varz:
            mol_new.translate(
                [
                    rnd.uniform(-a/2, a/2),
                    rnd.uniform(-a/2, a/2),
                    rnd.uniform(max(0., a*depz-clash_distance), a*depz)
                ]
            )
            depz = depz + depz_step
        else:
            mol_new.translate(
                [
                    rnd.uniform(-a/2, a/2),
                    rnd.uniform(-a/2, a/2),
                    rnd.uniform(-a/2*depz, a/2*depz)
                ]
            )
        mol_new.euler_rotate(
            phi=rnd.uniform(-180., 180.),
            theta=rnd.uniform(-90., 90.),
            psi=rnd.uniform(-180., 180.),
            center='COM'
        )
        mol_new_com = mol_new.get_center_of_mass()
        distances = []
        for molecule in morphology_list:
            distlist = [mol_new_com-molecule.get_center_of_mass()]
            distances.append(find_mic(distlist, cell, pbc)[1].tolist()[0])
        if all(distance > clash_distance for distance in distances):
            morphology_stack += mol_new
            if vdw_clash(morphology_stack, natoms):
                # remove the just added molecule
                del morphology_stack[-natoms:]
                clashed += 1
            else:
                morphology_list.append(mol_new)
                inserted += 1
        else:
            clashed += 1

    return morphology_list


def deposit_random(mol, parameters):
    """ Deposition of molecules of one type in a box. The molecules get random
    positions and orientations and are all accepted """
    trials = parameters['trials']
    a = parameters['lattice parameter']

    mol.set_cell([a, a, a])
    mol.set_pbc((1, 1, 1))
    mol.center(about=([a/2, a/2, a/2]))

    morphology_list = [mol.copy()]

    rnd.seed(1)

    trial = 0
    while trial < trials:
        trial += 1
        mol_new = mol.copy()
        mol_new.translate(
            [
                rnd.uniform(-a/2, a/2),
                rnd.uniform(-a/2, a/2),
                rnd.uniform(-a/2, a/2)
            ]
        )
        mol_new.euler_rotate(
            phi=rnd.uniform(-180., 180.),
            theta=rnd.uniform(-90., 90.),
            psi=rnd.uniform(-180., 180.),
            center='COM'
        )
        morphology_list.append(mol_new)

    return morphology_list


def gyration_radius(positions):
    """ calculate radius of gyration of particles with provided positions """
    from math import sqrt
    centroid = np.mean(positions, axis=0)
    rog = sqrt(np.mean((np.linalg.norm(positions-centroid, axis=1))**2, axis=0))
    return rog
