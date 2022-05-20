import pytest
import numpy as np
from ase import Atoms
from calorine.nepy.nep import get_descriptors, get_potential_forces_and_virials, _clean_tmp_dir

PbTe = Atoms('TePb', positions=[(0, 0, 0), (0, 0.0, 1.1)],
             cell=([100, 0, 0], [0, 100, 0], [0, 0, 100]))
C = Atoms('C', positions=[(0, 0, 0)])
CO = Atoms('CO', positions=[(0, 0, 0), (0, 0.0, 1.1)])
CC = Atoms('CC', positions=[(0, 0, 0), (0, 0.0, 1.1)])
CON = Atoms('CON', positions=[(0, 0, 0), (0, 0.0, 1.1), (0, 0.0, 2.2)])


def _load_nep_from_file(file: str) -> str:
    """Load a NEP model from file into a stringified version

    Parameters
    ----------
    file
        Path to nep.txt.

    Returns
    -------
    str
        Stringified NEP model.
    """
    with open(file, 'r') as f:
        model = f.read()
    return model


# --- get_descriptors ---
def test_get_descriptors_setup_dummy_NEP2_model():
    """Verifies the dummy NEP model is properly formatted."""
    get_descriptors(PbTe, debug=True)
    tmp_dir = './tmp_nepy/'
    PbTe_dummy = _load_nep_from_file(f'{tmp_dir}/nep.txt')
    _clean_tmp_dir(tmp_dir)
    expected_PbTe_dummy = _load_nep_from_file(
        'tests/nep_models/PbTe_NEP2_dummy.txt')
    assert PbTe_dummy == expected_PbTe_dummy


def test_get_descriptors_no_cell():
    """Should get descriptors for atoms without a specified cell, and raise a warning."""
    with pytest.warns(UserWarning) as record:
        descriptors = get_descriptors(CO)
    assert len(record) == 1
    assert record[0].message.args[0] == 'Using default unit cell (box with side 100 Å).'
    assert descriptors.shape == (2, 52)


def test_get_descriptors_NEP2_independent_of_species():
    """NEP2 should give the same descriptors regardless of atom species."""
    descriptors_PbTe = get_descriptors(PbTe)
    descriptors_CO = get_descriptors(CO)
    assert np.allclose(descriptors_CO, descriptors_PbTe, atol=1e-12, rtol=0)


def test_get_descriptors_NEP2_several_atoms_same_species():
    """NEP2 should get the descritors for a single component system"""
    descriptors_CC = get_descriptors(CC)
    assert descriptors_CC.shape == (2, 52)
    assert descriptors_CC.dtype == np.float64
    assert not np.all(np.isclose(descriptors_CC, 0))


def test_get_descriptors_dummy_NEP2_several_atom_species():
    """Verifies the dummy NEP model has the correct number of parameters."""
    # C
    get_descriptors(C, debug=True)
    tmp_dir = './tmp_nepy/'
    C_dummy_parameters = _load_nep_from_file(f'{tmp_dir}/nep.txt').split('\n')[6:]
    _clean_tmp_dir(tmp_dir)
    assert len(C_dummy_parameters) == 1698
    # CO
    get_descriptors(CO, debug=True)
    tmp_dir = './tmp_nepy/'
    CO_dummy_parameters = _load_nep_from_file(f'{tmp_dir}/nep.txt').split('\n')[6:]
    _clean_tmp_dir(tmp_dir)
    assert len(CO_dummy_parameters) == 1773
    # CON
    get_descriptors(CON, debug=True)
    tmp_dir = './tmp_nepy/'
    CON_dummy_parameters = _load_nep_from_file(f'{tmp_dir}/nep.txt').split('\n')[6:]
    _clean_tmp_dir(tmp_dir)
    assert len(CON_dummy_parameters) == 1898


def test_get_descriptors_NEP2_dummy():
    """Case: No NEP model supplied; using dummy NEP2 model.
       Compares results to output from `nep_cpu`
    """
    descriptors_PbTe = get_descriptors(PbTe)
    expected_PbTe = np.loadtxt(
        'tests/expected_descriptors/PbTe_2atom_NEP2_dummy.out')
    assert np.allclose(descriptors_PbTe, expected_PbTe, atol=1e-12, rtol=0)


def test_get_descriptors_NEP3():
    """Case: NEP3 model supplied. Compares results to output from `nep_cpu`"""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    descriptors_PbTe = get_descriptors(PbTe, potential_filename=nep3)
    expected_PbTe = np.loadtxt(
        'tests/expected_descriptors/PbTe_2atom_NEP3.out')
    assert np.allclose(descriptors_PbTe, expected_PbTe, atol=1e-12, rtol=0)


def test_get_descriptors_debug():
    """Check that the generated files are accessible in the debug directory"""
    get_descriptors(PbTe, debug=True)
    tmp_dir = './tmp_nepy/'
    PbTe_dummy = _load_nep_from_file(f'{tmp_dir}/nep.txt')
    _clean_tmp_dir(tmp_dir)
    assert 'nep 2 Te Pb' in PbTe_dummy


def test_get_descriptors_debug_directory_exists():
    """Should fail if debug directory already exists from an earlier calculation"""
    get_descriptors(PbTe, debug=True)
    tmp_dir = './tmp_nepy/'
    with pytest.raises(FileExistsError)as e:
        get_descriptors(PbTe, debug=True)
    assert 'Please delete or move the conflicting directory' in str(e)
    _clean_tmp_dir(tmp_dir)


# --- get_potential_forces_and_virials ---
def test_get_potential_forces_and_virials_NEP3():
    """Case: NEP3 model supplied. Compares results to output from `nep_cpu`"""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    energies, forces, virials = get_potential_forces_and_virials(
        PbTe, potential_filename=nep3)
    assert energies.shape == (2,)
    assert forces.shape == (2, 3)
    assert virials.shape == (2, 9)
    expected_forces = np.loadtxt(
        'tests/expected_descriptors/PbTe_2atom_NEP3_force.out')
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_NEP3_debug():
    """Compares result with debug flag enabled."""
    nep3 = 'tests/nep_models/PbTe_NEP3.txt'
    energies, forces, virials = get_potential_forces_and_virials(
        PbTe, potential_filename=nep3, debug=True)
    assert energies.shape == (2,)
    assert forces.shape == (2, 3)
    assert virials.shape == (2, 9)
    expected_forces = np.loadtxt(
        'tests/expected_descriptors/PbTe_2atom_NEP3_force.out')
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_dummy_NEP2():
    """Dummy NEP2 model supplied. Compares results to output from `nep_cpu` for another system"""
    nep3 = 'tests/nep_models/CO_NEP2_dummy.txt'
    energies, forces, virials = get_potential_forces_and_virials(
        CO, potential_filename=nep3)
    assert energies.shape == (2,)
    assert forces.shape == (2, 3)
    assert virials.shape == (2, 9)
    expected_forces = np.loadtxt(
        'tests/expected_descriptors/CO_2atom_NEP2_dummy_force.out')
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_no_cell():
    """Should work with default cell if no cell is supplied"""
    nep2_dummy = 'tests/nep_models/CO_NEP2_dummy.txt'
    with pytest.warns(UserWarning) as record:
        energies, forces, virials = get_potential_forces_and_virials(
            CO, potential_filename=nep2_dummy)
    assert len(record) == 1
    assert record[0].message.args[0] == 'Using default unit cell (box with side 100 Å).'
    assert energies.shape == (2,)
    assert forces.shape == (2, 3)
    assert virials.shape == (2, 9)
    expected_forces = np.loadtxt(
        'tests/expected_descriptors/CO_2atom_NEP2_dummy_force.out')
    assert np.allclose(forces, expected_forces, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_several_of_same_species():
    """Check that forces are correct for a CC system"""
    nep = 'tests/nep_models/C_NEP2_dummy.txt'
    energies, forces, virials = get_potential_forces_and_virials(
        CC, potential_filename=nep)
    assert energies.shape == (2,)
    assert forces.shape == (2, 3)
    assert virials.shape == (2, 9)
    expected_forces_PbTe = np.loadtxt(
        'tests/expected_descriptors/C_2atom_NEP2_dummy_force.out')
    assert np.allclose(forces, expected_forces_PbTe, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_several_different_species():
    """Check that forces are correct for a CON system.
    Note that these forces should be exactly zero for this system
    since the NEP2 dummy potential treats all atom species as identical atm.
    """
    nep = 'tests/nep_models/CON_NEP2_dummy.txt'
    energies, forces, virials = get_potential_forces_and_virials(
        CON, potential_filename=nep)
    assert energies.shape == (3,)
    assert forces.shape == (3, 3)
    assert virials.shape == (3, 9)
    expected_forces_PbTe = np.loadtxt(
        'tests/expected_descriptors/CON_3atom_NEP2_dummy_force.out')
    assert np.allclose(forces, expected_forces_PbTe, atol=1e-12, rtol=0)


def test_get_potential_forces_and_virials_no_potential():
    """Tries to get potentials, forces and virials without specifying potential"""
    with pytest.raises(ValueError)as e:
        get_potential_forces_and_virials(PbTe)
    assert 'Potential must be defined!' in str(e)
