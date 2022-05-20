from ase import Atoms
from ase.io import read, write
import pytest
import numpy as np
from ase.build import bulk
from calorine.io import read_settings, read_loss, read_nep, \
    read_thermo, read_kappa, read_hac, read_xyz, write_xyz


# --- read_settings ---
def test_read_settings_run_nvt():
    """Reads a run.in file with an NVT ensemble"""
    settings = read_settings('tests/example_files/run.in')
    assert settings['dump_hnemd'] == 1
    assert settings['Fe_x'] == 2
    assert settings['Fe_y'] == 3
    assert settings['Fe_z'] == 4

    assert settings['sampling_interval'] == 100
    assert settings['correlation_steps'] == 666
    assert settings['output_interval'] == 200

    assert settings['ensemble'] == 'nvt'
    assert settings['temperature'] == 300
    assert settings['temperature_final'] == 400
    assert settings['thermostat_coupling'] == 1

    assert settings['time_step'] == 1
    assert settings['dump_thermo'] == 2
    assert settings['neighbor'] == 66
    assert settings['dump_position'] == 3
    assert settings['velocity'] == 123
    assert settings['run'] == 1337


def test_read_settings_run_npt(tmpdir):
    """Reads a run.in file with an NPT ensemble"""
    p = tmpdir.join('run.in')
    p.write('ensemble npt 300 400 1 100 200 300 4\n')
    settings = read_settings(f'{p}')
    assert settings['ensemble'] == 'npt'
    assert settings['temperature'] == 300
    assert settings['temperature_final'] == 400
    assert settings['thermostat_coupling'] == 1
    assert settings['pressure_x'] == 100
    assert settings['pressure_y'] == 200
    assert settings['pressure_z'] == 300
    assert settings['pressure_coupling'] == 4


def test_read_settings_run_heat(tmpdir):
    """Reads a run.in file for heat transport"""
    p = tmpdir.join('run.in')
    p.write('ensemble heat 300 1 20 A B\ntime_step 0.1\n')
    settings = read_settings(f'{p}')
    assert settings['ensemble'] == 'heat'
    assert settings['temperature'] == 300
    assert settings['thermostat_coupling'] == 1
    assert settings['delta_temperature'] == 20
    assert settings['label_source'] == 'A'
    assert settings['label_sink'] == 'B'
    assert settings['time_step'] == 0.1


def test_read_settings_fcp_potential(tmpdir):
    """Reads a run.in file with a fcp potential"""
    p = tmpdir.join('run.in')
    p.write('potential tests/example_files/fcp/fcp.txt\n')
    settings = read_settings(f'{p}')
    assert settings['fcp_order'] == 2


def test_read_settings_run_nep_potential(tmpdir):
    """Reads a run.in file with a nep potential. At the moment only saves the filename."""
    p = tmpdir.join('run.in')
    p.write('potential tests/example_files/nep.txt\n')
    settings = read_settings(f'{p}')
    assert settings['potential'] == 'tests/example_files/nep.txt'


def test_read_settings_run_invalid_potential(tmpdir):
    """Tries to read a run.in file with an invalid potential"""
    p = tmpdir.join('run.in')
    run_invalid = tmpdir.join('fcp.txt')
    p.write(f'potential {run_invalid}\n')
    with pytest.raises(IOError) as e:
        read_settings(f'{p}')
    assert f'Failed to read fcp potential in file {run_invalid}' in str(e)


def test_read_settings_unknown_setting(tmpdir):
    """Reads a run.in file with a comment"""
    p = tmpdir.join('run.in')
    p.write('test 1\n')
    settings = read_settings(f'{p}')
    assert settings['test'] == '1'


def test_read_settings_run_comment(tmpdir):
    """Reads a run.in file with a comment"""
    p = tmpdir.join('run.in')
    p.write('#ensemble heat 300 1 20 A B\n')
    settings = read_settings(f'{p}')
    assert settings == {}


def test_read_settings_run_blank_line(tmpdir):
    """Reads a run.in file with a blank line"""
    p = tmpdir.join('run.in')
    p.write('\n')
    settings = read_settings(f'{p}')
    assert settings == {}


def test_read_settings_invalid_ensemble(tmpdir):
    """Tries to read a run.in with invalid ensemble"""
    p = tmpdir.join('run.in')
    p.write('ensemble hmm\n')
    with pytest.raises(ValueError) as e:
        read_settings(f'{p}')
    error_string = 'Run.in contains invalid ensemble hmm. '\
        'Expected nvt, npt or heat.'
    assert error_string in str(e)


def test_read_settings_nep():
    """Reads a nep.in file"""
    settings = read_settings('tests/example_files/nep.in')
    assert settings['version'] == '4'
    assert settings['type'] == '2 C H'
    assert settings['cutoff'] == '8 4'
    assert settings['n_max'] == '8 6'
    assert settings['l_max'] == '4'
    assert settings['neuron'] == '50'
    assert settings['lambda_1'] == '0.01'
    assert settings['lambda_2'] == '0.01'
    assert settings['batch'] == '100'
    assert settings['population'] == '50'
    assert settings['generation'] == '50000'
    assert settings['lambda_e'] == '1'
    assert 'lambda_f' not in settings.keys()


def test_read_settings_nep_blank_line(tmpdir):
    """Reads a nep.in file with a blank line"""
    p = tmpdir.join('nep.in')
    p.write('\n')
    settings = read_settings(f'{p}')
    assert settings == {}


def test_read_settings_unknown_format(tmpdir):
    """Tries to read an unknown file format"""
    p = tmpdir.join('run_invalid.in')
    with pytest.raises(ValueError) as e:
        read_settings(f'{p}')
    assert f'Unknown configuration file format for {p}' in str(e)


# --- read_loss ---
def test_read_loss():
    """Reads a loss.out file"""
    loss = read_loss('tests/example_files/loss.out')
    columns_check = loss.columns == ['total_loss', 'L1', 'L2',
                                     'RMSE_E_train', 'RMSE_F_train', 'RMSE_V_train',
                                     'RMSE_E_test', 'RMSE_F_test', 'RMSE_V_test']
    assert columns_check.all()
    assert isinstance(loss.index[0], int)
    assert loss.index[0] == 100
    assert len(loss) == 95


def test_read_loss_single_row(tmpdir):
    """Tries to read a loss.out file that has only a single row"""
    p = tmpdir.join('loss.out')
    p.write('100 2 3 4 5 6 7 8 9 10\n')
    loss = read_loss(f'{p}')
    columns_check = loss.columns == ['total_loss', 'L1', 'L2',
                                     'RMSE_E_train', 'RMSE_F_train', 'RMSE_V_train',
                                     'RMSE_E_test', 'RMSE_F_test', 'RMSE_V_test']
    assert columns_check.all()
    assert isinstance(loss.index[0], int)
    assert loss.index[0] == 100


def test_read_loss_malformed_file(tmpdir):
    """Tries to read a malformed loss.out file"""
    p = tmpdir.join('loss_invalid.out')
    p.write('0 0 0 0 0 0\n')
    with pytest.raises(ValueError):
        read_loss(f'{p}')


# --- read_nep ---
def test_read_nep():
    """Reads a NEP3 nep.txt file"""
    settings, parameters = read_nep('tests/example_files/nep.txt')
    assert settings['zbl'] == (1, 2)
    assert settings['cutoff'] == (8, 4)
    assert settings['n_max'] == (4, 4)
    assert settings['l_max'] == (4, 2, 0)
    assert settings['basis_size'] == (8, 8)
    assert settings['ANN'] == (30, 0)
    assert len(parameters) == 1350


def test_read_nep_malformed_file(tmpdir):
    """Tries to read an invalid nep.in file"""
    p = tmpdir.join('nep.in')
    p.write("""nep123 x x\nnep123 x x\nnep123 x x\nnep123 x x\nnep123 x x\nnep123 x x\n
            nep123 x x\nnep123 x x\n  6.2799901e-02""")
    with pytest.raises(IOError):
        read_nep(f'{p}')


# --- read_kappa ---
def test_read_kappa():
    """Reads a kappa.out file"""
    kappa = read_kappa('tests/example_files/kappa.out')
    columns_check = kappa.columns == ['kx_in', 'kx_out', 'ky_in', 'ky_out',
                                      'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(kappa.index[0], int)
    assert isinstance(kappa['kx_in'][0], np.float64)
    assert kappa.index[0] == 0


def test_read_kappa_single_row(tmpdir):
    """Reads a single row kappa.out file"""
    p = tmpdir.join('kappa.out')
    p.write('0 1 2 3 4\n')
    kappa = read_kappa(f'{p}')
    columns_check = kappa.columns == ['kx_in', 'kx_out', 'ky_in', 'ky_out',
                                      'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(kappa.index[0], int)
    assert isinstance(kappa['kx_in'][0], np.float64)
    assert kappa.index[0] == 0


def test_read_kappa_nan():
    """Reads a kappa.out file filed with nans. Should this raise a warning?"""
    kappa = read_kappa('tests/example_files/kappa_nan.out')
    columns_check = kappa.columns == ['kx_in', 'kx_out', 'ky_in', 'ky_out',
                                      'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(kappa.index[0], int)
    assert isinstance(kappa['kx_in'][0], np.float64)
    assert kappa.index[0] == 0


def test_read_kappa_malformed_file(tmpdir):
    """Tries to read a malformed kappa.out file"""
    p = tmpdir.join('kappa_invalid.out')
    p.write('0 0 0 0 0 0 0 0 0 0 \n')
    with pytest.raises(ValueError):
        read_kappa(f'{p}')


# --- read_hac ---
def test_read_hac():
    """Reads a hac.out file"""
    hac = read_hac('tests/example_files/hac.out')
    columns_check = hac.columns == ['time', 'kx_out', 'ky_out',
                                    'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(hac.index[0], int)
    assert isinstance(hac['time'][0], np.float64)
    assert hac.index[0] == 0


def test_read_hac_single_row(tmpdir):
    """Reads a single row hac.out file"""
    p = tmpdir.join('hac.out')
    p.write('0 1 2 3 4 5 6 7 8 9 10\n')
    hac = read_hac(f'{p}')
    columns_check = hac.columns == ['time', 'kx_out', 'ky_out',
                                    'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(hac.index[0], int)
    assert isinstance(hac['time'][0], np.float64)
    assert hac.index[0] == 0


def test_read_hac_nan():
    """Reads a hac.out file filed with nans. Should this raise a warning?"""
    hac = read_hac('tests/example_files/hac_nan.out')
    columns_check = hac.columns == ['time', 'kx_out', 'ky_out',
                                    'kz_tot', 'kx_tot', 'ky_tot']
    assert columns_check.all()
    assert isinstance(hac.index[0], int)
    assert isinstance(hac['time'][0], np.float64)
    assert hac.index[0] == 0


def test_read_hac_malformed_file(tmpdir):
    """Tries to read a malformed hac.out file"""
    p = tmpdir.join('hac_invalid.out')
    p.write('0 0 0 \n')
    with pytest.raises(ValueError):
        read_hac(f'{p}')


# --- read_thermo ---
def test_read_thermo_orthorhombic():
    """Reads a thermo.out file with an orthorhombic structure"""
    thermo = read_thermo('tests/example_files/thermo_ortho.out')
    columns_check = thermo.columns == ['temperature', 'kinetic_energy', 'potential_energy',
                                       'Px', 'Py', 'Pz',
                                       'Lx', 'Ly', 'Lz']
    assert columns_check.all()


def test_read_thermo_triclinic():
    """Reads a thermo.out file with an triclinic structure"""
    thermo = read_thermo('tests/example_files/thermo_tri.out')
    columns_check = thermo.columns == ['temperature', 'kinetic_energy', 'potential_energy',
                                       'Px', 'Py', 'Pz',
                                       'h_xx', 'h_xy', 'h_xz',
                                       'h_yx', 'h_yy', 'h_yz',
                                       'h_zx', 'h_zy', 'h_zz'
                                       ]
    assert columns_check.all()


def test_read_thermo_malformed_file(tmpdir):
    """Tries to read a malformed thermo.out file"""
    p = tmpdir.join('termo_invalid.out')
    p.write('NaN NaN NaN NaN NaN NaN\n')
    with pytest.raises(ValueError):
        read_thermo(f'{p}')


# --- read_xyz and write_xyz ---
def test_write_read_xyz(tmpdir):
    """Writes and reads xyz files"""

    use_triclinic = True

    f = tmpdir.join('atoms.xyz')
    structure_orig = bulk('C').repeat(3)
    write_xyz(f, structure_orig)
    res = read_xyz(f)
    assert isinstance(res, tuple)

    structure_read, settings_read = res
    assert len(structure_orig) == len(structure_read)
    assert np.allclose(structure_orig.cell, structure_read.cell)
    assert np.allclose(structure_orig.positions, structure_read.positions)
    assert isinstance(settings_read, dict)

    cutoff = 9.0
    maximum_neighbors = 99
    write_xyz(f, structure_orig, cutoff=cutoff,
              maximum_neighbors=maximum_neighbors, use_triclinic=use_triclinic)
    res = read_xyz(f)
    structure_read, settings_read = res

    assert np.isclose(settings_read['cutoff'], cutoff)
    assert settings_read['maximum_neighbors'] == maximum_neighbors
    assert settings_read['use_triclinic'] == use_triclinic
    assert not settings_read['has_velocity']

    cutoff = 9.0
    write_xyz(f, structure_orig, cutoff=cutoff)
    res = read_xyz(f)
    structure_read, settings_read = res

    assert np.isclose(settings_read['cutoff'], cutoff)
    assert settings_read['maximum_neighbors'] == 1024
    assert settings_read['use_triclinic']
    assert not settings_read['has_velocity']


def test_write_read_xyz_orthorhombic_has_velocity(tmpdir):
    """Writes and reads an orthorhombic structure with velocity"""
    use_triclinic = False
    f = tmpdir.join('atoms.xyz')
    structure = Atoms('CCC', positions=[(0, 0, 0), (0, 0, 1.1), (0, 0, 2.2)], cell=[1, 2, 3])
    structure.set_velocities([[0, 0, 100], [0, 0, 150], [0, 0, 200]])
    write_xyz(f, structure, use_triclinic=use_triclinic)
    res = read_xyz(f)

    _, settings_read = res
    assert not settings_read['use_triclinic']
    assert settings_read['has_velocity']


def test_write_read_xyz_groupings(tmpdir):
    """Writes and reads a structure with groups"""
    f = tmpdir.join('atoms.xyz')
    structure = Atoms('CCCC',
                      positions=[(0, 0, 0), (0, 0, 1.1), (0, 0, 2.2), (0, 0, 3.3)],
                      cell=[1, 2, 3])
    write_xyz(f, structure, groupings=[[[0, 1], [2, 3]], [[0], [1, 2, 3]]])
    res = read_xyz(f)

    _, settings_read = res
    assert settings_read['number_of_groups'] == 2


def test_write_xyz_invalid_groupings(tmpdir):
    """Tries to write with invalid groups"""
    f = tmpdir.join('atoms.xyz')
    structure = Atoms('CCC', positions=[(0, 0, 0), (0, 0, 1.1), (0, 0, 2.2)], cell=[1, 2, 3])
    with pytest.raises(ValueError):
        # Too many groupings
        write_xyz(f, structure, groupings=[[[0, 1], [2]], [
                  [0, 1], [2]], [[0, 1], [2]], [[0, 1], [2]]])
    with pytest.raises(ValueError):
        # Number of atoms do not add up to the total
        write_xyz(f, structure, groupings=[[[0, 1], [1, 2]]])


# --- Check dump.xyz ---
# Not a unit test, but a good FYI test for our sake
def test_ase_correctly_parses_dump(tmpdir):
    """Check that ASE can correctly read dump files"""
    dump_file = 'tests/example_files/md_no_velocities_or_forces/dump.xyz'
    snapshots = read(dump_file, index=':')
    traj = tmpdir.join('lmao.traj')
    write(f'{traj}', snapshots)  # Make sure that writing works without crashing
    assert all(snapshots[-1][-1].position == [3.10105816, 2.94360168, 2.68268773])


def test_ase_correctly_parses_dump_forces_and_velocities(tmpdir):
    """Check that ASE can correctly read dump files with forces and velocities"""
    dump_file = 'tests/example_files/md_velocities_and_forces/dump.xyz'
    snapshots = read(dump_file, index=':')
    traj = tmpdir.join('lmao.traj')
    write(f'{traj}', snapshots)  # Make sure that writing works without crashing
    assert all(snapshots[-1][-1].position == [3.24197501, 2.84584855, 2.89100032])
    assert all(snapshots[-1].get_array('vel')[-1] == [-0.00033243, 0.00061451, 0.00044743])
    assert all(snapshots[-1].get_array('forces')[-1] == [-0.96089202, -0.01649800, -0.11494368])
