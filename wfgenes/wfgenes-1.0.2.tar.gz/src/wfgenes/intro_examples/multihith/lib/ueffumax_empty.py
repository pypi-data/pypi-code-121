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

from parsl import python_app
from time import sleep
from datetime import datetime


@python_app
def MERGE(**kwargs):
    dic_merged = {}
    for key, value in kwargs.items():
        if isinstance(value, np.number):
            value = float(value)
        else:
            value = value
    return (kwargs)            


@python_app
def build_structure_generic(params):
    struct_dict = []
    sleep(2)
    return struct_dict

@python_app
def build_structure(params):
    """ construct a slab model and add adsorbates """
    struct_dict = []
    sleep(2)
    return struct_dict

@python_app
def structure_relaxation(params, struct_dict):
    now = datetime.now()
    print( now.strftime("%H:%M:%S"))
    """ perform structure relaxation with constraints """
    struct_dict = ['test']
    energy = []
    forces = []
    dipole = []
    sleep(2)
    return struct_dict, energy, forces, dipole

@python_app
def vibrations(params, struct_dict):
    """ perform normal mode analysis with constraints """
    # calculate properties
    entropy = 0
    partfun = 0
    vet = 0
    zpe = 0
    tst = 0
    minimum = 0
    vib_ene_real = 0
    sleep(2)
    return vib_ene_real, entropy, vet, partfun, zpe, tst, minimum

@python_app
def reaction_energies(props, reactions):
    """ calculate reaction energies """
    sleep(2)
    return reactions





