#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `utils` module."""

import pytest  # noqa: F401
import read_structure_step  # noqa: F401
from . import build_filenames

from molsystem.system_db import SystemDB

bond_string = """\
    i   j  bondorder
1   1   2          1
2   1   5          1
3   1   7          1
4   2   3          2
5   3   4          1
6   3   6          1
7   4   5          2
8   5   8          1
9   6   9          1
10  6  10          1"""
xyz_bond_string = """\
    i   j  bondorder
1   1   7          1
2   5   8          1
3   1   5          1
4   1   2          1
5   4   5          2
6   2   3          2
7   3   4          1
8   3   6          1
9   6  10          1
10  6   9          1"""
acetonitrile_bonds = """\
   i  j  bondorder
1  2  5          1
2  2  4          1
3  1  2          1
4  1  6          3
5  2  3          1"""


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


@pytest.mark.parametrize(
    "structure", ["3TR_model.mol2", "3TR_model.xyz", "3TR_model.pdb", "3TR_model.sdf"]
)
def test_format(configuration, structure):

    file_name = build_filenames.build_data_filename(structure)
    read_structure_step.read(file_name, configuration)

    assert configuration.n_atoms == 10
    assert all(
        atom in ["N", "N", "N", "N", "C", "C", "H", "H", "H", "H"]
        for atom in configuration.atoms.symbols
    )
    coordinates = configuration.atoms.coordinates
    assert len(coordinates) == 10
    assert all(len(point) == 3 for point in coordinates)
    assert configuration.bonds.n_bonds == 10
    if "xyz" in structure:
        if str(configuration.bonds) != xyz_bond_string:
            print(configuration.bonds)
        assert str(configuration.bonds) == xyz_bond_string
    else:
        if str(configuration.bonds) != bond_string:
            print(configuration.bonds)
        assert str(configuration.bonds) == bond_string


@pytest.mark.skipif(
    read_structure_step.formats.mop.find_mopac.find_mopac() is None,
    reason="MOPAC could not be found",
)
def test_mopac(configuration):

    file_name = build_filenames.build_data_filename("acetonitrile.mop")
    read_structure_step.read(file_name, configuration)

    assert configuration.n_atoms == 6
    assert all(
        atom in ["H", "H", "H", "C", "C", "N"] for atom in configuration.atoms.symbols
    )
    coordinates = configuration.atoms.coordinates
    assert len(coordinates) == 6
    assert all(len(point) == 3 for point in coordinates)
    assert configuration.bonds.n_bonds == 5
    if str(configuration.bonds) != acetonitrile_bonds:
        print(configuration.bonds)
    assert str(configuration.bonds) == acetonitrile_bonds


@pytest.mark.skipif(
    read_structure_step.formats.mop.find_mopac.find_mopac() is None,
    reason="MOPAC could not be found",
)
def test_mopac_2(configuration):
    check_symbols = ["Li", "F", "Li", "F", "Li", "F"]
    check_smiles = "[Li]F.[Li]F.[Li]F"
    file_name = build_filenames.build_data_filename("lithium fluoride, trimer.mop")
    read_structure_step.read(file_name, configuration)

    if configuration.atoms.symbols != check_symbols:
        print(configuration.atoms.symbols)
    smiles = configuration.canonical_smiles
    if smiles != check_smiles:
        print(smiles)

    assert configuration.atoms.symbols == check_symbols
    assert smiles == check_smiles


@pytest.mark.skipif(
    read_structure_step.formats.mop.find_mopac.find_mopac() is None,
    reason="MOPAC could not be found",
)
def test_mopac_3(configuration):
    check_symbols = [
        "Cu",
        "Cu",
        "Cu",
        "Cu",
        "Br",
        "Br",
        "Br",
        "Br",
        "Br",
        "Br",
        "Br",
        "Br",
        "Br",
        "Br",
    ]
    check_smiles = "Br[Cu]([Cu][Cu](Br)(Br)(Br)Br)(Br)Br.Br[Cu](Br)Br"
    file_name = build_filenames.build_data_filename("Cu(II)4Br10(2-) (CIVNAW10).mop")
    read_structure_step.read(file_name, configuration)

    if configuration.atoms.symbols != check_symbols:
        print(configuration.atoms.symbols)
    smiles = configuration.canonical_smiles
    if smiles != check_smiles:
        print(smiles)

    assert configuration.atoms.symbols == check_symbols
    assert smiles == check_smiles


@pytest.mark.skipif(
    read_structure_step.formats.mop.find_mopac.find_mopac() is None,
    reason="MOPAC could not be found",
)
def test_mopac_4(configuration):
    check_symbols = [
        "Eu",
        "N",
        "N",
        "N",
        "N",
        "N",
        "N",
        "O",
        "O",
        "O",
        "O",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
    ]
    check_smiles = (
        r"C[C]1c2cccc(n2)/C(=N/CC[N@]2[Eu]34([N@@]1CC/N=C(\C)/c1nc([C]2C)ccc1)"
        r"(O[C](O3)C)O[C](O4)C)/C"
    )
    file_name = build_filenames.build_data_filename(
        "RM1 63 Europium, CCDC entry LAPJAN.mop"
    )
    read_structure_step.read(file_name, configuration)

    if configuration.atoms.symbols != check_symbols:
        print(configuration.atoms.symbols)
    smiles = configuration.canonical_smiles
    if smiles != check_smiles:
        print(smiles)

    assert configuration.atoms.symbols == check_symbols
    assert smiles == check_smiles


@pytest.mark.skipif(
    read_structure_step.formats.mop.find_mopac.find_mopac() is None,
    reason="MOPAC could not be found",
)
def test_mopac_6(configuration):
    check_symbols = ["F", "K", "F", "K"]
    check_smiles = "F[K].F[K]"
    file_name = build_filenames.build_data_filename("potassium fluoride, dimer.mop")
    read_structure_step.read(file_name, configuration)

    if configuration.atoms.symbols != check_symbols:
        print(configuration.atoms.symbols)
    smiles = configuration.canonical_smiles
    if smiles != check_smiles:
        print(smiles)

    assert configuration.atoms.symbols == check_symbols
    assert smiles == check_smiles


@pytest.mark.skipif(
    read_structure_step.formats.mop.find_mopac.find_mopac() is None,
    reason="MOPAC could not be found",
)
def test_mopac_7(configuration):
    check_symbols = [
        "Cr",
        "O",
        "O",
        "O",
        "O",
        "O",
        "O",
        "C",
        "C",
        "C",
        "C",
        "C",
        "C",
        "Cr",
        "C",
        "C",
        "O",
        "O",
        "O",
        "O",
        "O",
        "C",
        "C",
        "C",
        "O",
        "C",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
        "H",
    ]
    check_smiles = "C[C](O[Cr]12(OC(=O)C)O[C](O[Cr]2(O[C](O)C)(OC(=O)C)O[C](O1)C)C)O"
    file_name = build_filenames.build_data_filename("Cr_ACETCR.mop")
    read_structure_step.read(file_name, configuration)

    if configuration.atoms.symbols != check_symbols:
        print(configuration.atoms.symbols)
    smiles = configuration.canonical_smiles
    if smiles != check_smiles:
        print(smiles)

    assert configuration.atoms.symbols == check_symbols
    assert smiles == check_smiles


@pytest.mark.skipif(
    read_structure_step.formats.mop.find_mopac.find_mopac() is None,
    reason="MOPAC could not be found",
)
def test_mopac_8(configuration):
    check_symbols = [
        "C",
        "H",
    ]
    check_smiles = "[CH]"
    file_name = build_filenames.build_data_filename("methylidyne.mop")
    read_structure_step.read(file_name, configuration)

    if configuration.atoms.symbols != check_symbols:
        print(configuration.atoms.symbols)
    smiles = configuration.canonical_smiles
    if smiles != check_smiles:
        print(smiles)

    assert configuration.atoms.symbols == check_symbols
    assert smiles == check_smiles
