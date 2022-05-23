#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `utils` module."""

import pytest  # noqa: F401
import read_structure_step  # noqa: F401
from . import build_filenames

from molsystem.system_db import SystemDB

bond_string = """\
   i  j  bondorder
1  1  2          1
2  1  3          1"""


@pytest.fixture(scope="module")
def configuration():
    """Create a system db, system and configuration."""
    db = SystemDB(filename="file:seamm_db?mode=memory&cache=shared")
    system = db.create_system(name="default")
    configuration = system.create_configuration(name="default")

    yield configuration

    db.close()
    try:
        del db
    except:  # noqa: E722
        print("Caught error deleting the database")


@pytest.mark.parametrize("file_name", ["spc.xyz", "spc"])
@pytest.mark.parametrize("extension", [None, ".xyz", "xyz", "XYZ", "xYz"])
def test_extensions(configuration, file_name, extension):

    xyz_file = build_filenames.build_data_filename(file_name)
    read_structure_step.read(xyz_file, configuration, extension=extension)

    assert configuration.n_atoms == 3
    assert all(atom in ["O", "H", "H"] for atom in configuration.atoms.symbols)

    coordinates = configuration.atoms.coordinates
    assert len(coordinates) == 3
    assert all(len(point) == 3 for point in coordinates)

    assert configuration.bonds.n_bonds == 2
    if str(configuration.bonds) != bond_string:
        print(configuration.bonds)
    assert str(configuration.bonds) == bond_string


def test_sanitize_file_format_regex_validation(configuration):

    with pytest.raises(NameError):
        read_structure_step.read("spc.xyz", configuration, extension=".xy-z")
