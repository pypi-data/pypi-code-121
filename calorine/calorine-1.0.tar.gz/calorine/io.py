from typing import Dict, List, Tuple

import numpy as np
from ase import Atoms
from ase.neighborlist import NeighborList
from pandas import DataFrame


def read_settings(filename: str) -> dict:
    """Returns the settings from a configuration file as a dictionary.

    Parameters
    ----------
    filename
        input file name
    """
    settings = {}
    if filename.endswith('run.in'):
        with open(filename) as f:
            for line in f.readlines():
                flds = line.split()
                if len(flds) == 0:
                    continue
                if flds[0].startswith('#'):
                    continue
                if flds[0] == 'compute_hnemd':
                    settings['dump_hnemd'] = int(flds[1])
                    settings['Fe_x'] = float(flds[2])
                    settings['Fe_y'] = float(flds[3])
                    settings['Fe_z'] = float(flds[4])
                elif flds[0] == 'compute_hac':
                    settings['sampling_interval'] = int(flds[1])
                    settings['correlation_steps'] = int(flds[2])
                    settings['output_interval'] = int(flds[3])
                elif flds[0] == 'ensemble':
                    settings['ensemble'] = flds[1]
                    if settings['ensemble'].startswith('nvt'):
                        settings['temperature'] = float(flds[2])
                        settings['temperature_final'] = float(flds[3])
                        settings['thermostat_coupling'] = float(flds[4])
                    elif settings['ensemble'].startswith('npt'):
                        settings['temperature'] = float(flds[2])
                        settings['temperature_final'] = float(flds[3])
                        settings['thermostat_coupling'] = float(flds[4])
                        settings['pressure_x'] = float(flds[5])
                        settings['pressure_y'] = float(flds[6])
                        settings['pressure_z'] = float(flds[7])
                        settings['pressure_coupling'] = float(flds[8])
                    elif settings['ensemble'].startswith('heat'):
                        settings['temperature'] = float(flds[2])
                        settings['thermostat_coupling'] = float(flds[3])
                        settings['delta_temperature'] = float(flds[4])
                        settings['label_source'] = flds[5]
                        settings['label_sink'] = flds[6]
                    else:
                        raise ValueError(f'Run.in contains invalid ensemble {settings["ensemble"]}.'
                                         f' Expected nvt, npt or heat.')
                elif flds[0] == 'time_step':
                    settings['time_step'] = float(flds[1])
                elif flds[0] == 'dump_thermo':
                    settings['dump_thermo'] = int(flds[1])
                elif flds[0] == 'neighbor':
                    settings['neighbor'] = int(flds[1])
                elif flds[0] == 'dump_position':
                    settings['dump_position'] = int(flds[1])
                elif flds[0] == 'velocity':
                    settings['velocity'] = float(flds[1])
                elif flds[0] == 'run':
                    settings['run'] = int(flds[1])
                elif flds[0] == 'potential':
                    settings[flds[0]] = ' '.join(flds[1:])
                    potential_filename = flds[1]
                    if 'fcp.txt' in potential_filename:
                        try:
                            with open(potential_filename, 'r') as f:
                                settings['fcp_order'] = int(f.readlines()[1].split()[0])
                        except IOError as e:
                            raise IOError(
                                f'Failed to read fcp potential in file {potential_filename}') from e
                else:
                    settings[flds[0]] = ' '.join(flds[1:])
    elif filename.endswith('nep.in'):
        with open(filename) as f:
            for line in f.readlines():
                flds = line.split()
                if len(flds) == 0:
                    continue
                if flds[0].startswith('#'):
                    continue
                settings[flds[0]] = ' '.join(flds[1:])
    else:
        raise ValueError(f'Unknown configuration file format for {filename}')
    return settings


def read_loss(filename: str) -> DataFrame:
    """Parses a file in ``loss.out`` format from GPUMD and returns the
    content as a data frame. More information concerning file format,
    content and units can be found at
    https://gpumd.zheyongfan.org/index.php/The_output_files_for_the_nep_executable#The_loss.out_file.

    Parameters
    ----------
    filename
        input file name

    """
    data = np.loadtxt(filename)
    if isinstance(data[0], np.float64):
        # If only a single row in loss.out, append a dimension
        data = data.reshape(1, -1)
    if len(data[0]) != 10:
        raise ValueError(f'Input file contains {len(data[0])} data columns.'
                         f' Expected 10 columns.')
    tags = 'total_loss L1 L2'
    tags += ' RMSE_E_train RMSE_F_train RMSE_V_train'
    tags += ' RMSE_E_test RMSE_F_test RMSE_V_test'
    generations = range(100, len(data) * 100 + 1, 100)
    df = DataFrame(data=data[:, 1:], columns=tags.split(), index=generations)
    return df


def read_nep(filename: str) -> Tuple[Dict[str, tuple], List[float]]:
    """Parses a file in ``nep.txt`` format from GPUMD and returns the
    content as a tuple of a dict and a list. The dict contains the
    information contained in the header, whereas the list contains the
    weights and rescaling factors.

    Parameters
    ----------
    filename
        input file name

    """
    header = []
    parameters = []
    nheader = 6
    with open(filename) as f:
        for k, line in enumerate(f.readlines()):
            flds = line.split()
            if len(flds) == 0:
                continue
            if k == 0 and 'zbl' in flds[0]:
                nheader += 1
            if k <= nheader:
                header.append(tuple(flds))
            elif len(flds) == 1:
                parameters.append(float(flds[0]))
            else:
                raise IOError(f'Failed to parse line {k} from {filename}')
    settings = {}
    for flds in header:
        if flds[0] in ['cutoff']:
            settings[flds[0]] = tuple(map(float, flds[1:]))
        elif flds[0] in ['zbl', 'n_max', 'l_max', 'ANN', 'basis_size']:
            settings[flds[0]] = tuple(map(int, flds[1:]))
        else:
            settings[flds[0]] = flds[1:]
    return settings, parameters


def read_kappa(filename: str) -> DataFrame:
    """Parses a file in ``kappa.out`` format from GPUMD and returns the
    content as a data frame. More information concerning file format,
    content and units can be found at
    https://gpumd.zheyongfan.org/index.php/The_kappa.out_output_file.

    Parameters
    ----------
    filename
        input file name

    """
    data = np.loadtxt(filename)
    if isinstance(data[0], np.float64):
        # If only a single row in kappa.out, append a dimension
        data = data.reshape(1, -1)
    tags = 'kx_in kx_out ky_in ky_out kz_tot'.split()
    if len(data[0]) != len(tags):
        raise ValueError(f'Input file contains {len(data[0])} data columns.'
                         f' Expected {len(tags)} columns.')
    df = DataFrame(data=data, columns=tags)
    df['kx_tot'] = df.kx_in + df.kx_out
    df['ky_tot'] = df.ky_in + df.ky_out
    return df


def read_hac(filename: str) -> DataFrame:
    """Parses a file in ``hac.out`` format from GPUMD and returns the
    content as a data frame. More information concerning file format,
    content and units can be found at
    https://gpumd.zheyongfan.org/index.php/The_hac.out_output_file.

    Parameters
    ----------
    filename
        input file name

    """
    data = np.loadtxt(filename)
    if isinstance(data[0], np.float64):
        # If only a single row in hac.out, append a dimension
        data = data.reshape(1, -1)
    tags = 'time'
    tags += ' jin_jtot_x jout_jtot_x jin_jtot_y jout_jtot_y jtot_jtot_z'
    tags += ' kx_in kx_out ky_in ky_out kz_tot'
    tags = tags.split()
    if len(data[0]) != len(tags):
        raise ValueError(f'Input file contains {len(data[0])} data columns.'
                         f' Expected {len(tags)} columns.')
    df = DataFrame(data=data, columns=tags)
    df['kx_tot'] = df.kx_in + df.kx_out
    df['ky_tot'] = df.ky_in + df.ky_out
    # remove columns with less relevant data to save space
    for col in df:
        if 'jtot' in col or '_in' in col:
            del df[col]
    return df


def read_thermo(filename: str,
                natoms: int = 1) -> DataFrame:
    """Parses a file in ``thermo.out`` format from GPUMD and returns the
    content as a data frame. More information concerning file format,
    content and units can be found at
    https://gpumd.zheyongfan.org/index.php/The_thermo.out_output_file.

    Parameters
    ----------
    filename
        input file name
    natoms
        number of atoms; used to normalize energies

    """
    data = np.loadtxt(filename)
    if isinstance(data[0], np.float64):
        # If only a single row in loss.out, append a dimension
        data = data.reshape(1, -1)
    if len(data[0]) == 9:
        # orthorhombic box
        tags = 'temperature kinetic_energy potential_energy'
        tags += ' Px Py Pz Lx Ly Lz'
    elif len(data[0]) == 15:
        # triclinic box
        tags = 'temperature kinetic_energy potential_energy'
        tags += ' Px Py Pz'
        tags += ' h_xx h_xy h_xz h_yx h_yy h_yz h_zx h_zy h_zz'
    else:
        raise ValueError(f'Input file contains {len(data[0])} data columns.'
                         f' Expected 9 or 15 columns.')
    df = DataFrame(data=data, columns=tags.split())
    assert natoms > 0, 'natoms must be positive'
    df.kinetic_energy /= natoms
    df.potential_energy /= natoms
    return df


def read_xyz(filename: str) -> Tuple[Atoms, Dict[str, int]]:
    """
    Read the structure input file (`xyz.in`) for GPUMD and return the
    structure along with run input parameters from the file.

    Parameters
    ----------
    filename
        Name of file from which to read the structure

    Returns
    -------
    tuple comprising the structure and the parameters from the first row of the file
    """

    with open(filename, 'r') as fd:

        # Parse first line
        first_line = next(fd)
        input_parameters = {}
        keys = ['number_of_atoms', 'maximum_neighbors', 'cutoff',
                'use_triclinic', 'has_velocity', 'number_of_groups']
        types = [float if key == 'cutoff' else int for key in keys]
        for k, (key, typ) in enumerate(zip(keys, types)):
            input_parameters[key] = typ(first_line.split()[k])

        # Parse second line
        second_line = next(fd)
        second_arr = np.array(second_line.split())
        pbc = second_arr[:3].astype(bool)
        if input_parameters['use_triclinic']:
            cell = second_arr[3:].astype(float).reshape((3, 3))
        else:
            cell = np.diag(second_arr[3:].astype(float))

        # Parse all remaining rows
        n_rows = input_parameters['number_of_atoms']
        n_columns = 5 + input_parameters['has_velocity'] * 3
        n_columns += input_parameters['number_of_groups']
        rest_lines = [next(fd) for _ in range(n_rows)]
        rest_arr = np.array([line.split() for line in rest_lines])
        assert rest_arr.shape == (n_rows, n_columns)

    # Extract atom types, positions and masses
    symbols = rest_arr[:, 0].astype('str')
    positions = rest_arr[:, 1:4].astype(float)

    # Create the Atoms object
    structure = Atoms(symbols=symbols, positions=positions, pbc=pbc, cell=cell)
    if input_parameters['has_velocity']:
        velocities = rest_arr[:, 5:8].astype(float)
        structure.set_velocities(velocities)
    if input_parameters['number_of_groups']:
        start_col = 5 + 3 * input_parameters['has_velocity']
        groups = rest_arr[:, start_col:].astype(int)
        structure.info = {i: {'groups': groups[i, :]} for i in range(n_rows)}

    return structure, input_parameters


def write_xyz(filename: str,
              structure: Atoms,
              maximum_neighbors: int = None,
              cutoff: float = None,
              groupings: List[List[List[int]]] = None,
              use_triclinic: bool = False):
    """
    Writes a structure into GPUMD input format (`xyz.in`).

    Parameters
    ----------
    filename
        Name of file to which the structure should be written
    structure
        Input structure
    maximum_neighbors
        Maximum number of neighbors any atom can ever have (not relevant when
        using force constant potentials)
    cutoff
        Initial cutoff distance used for building the neighbor list (not
        relevant when using force constant potentials)
    groupings
        Groups into which the individual atoms should be divided in the form of
        a list of list of lists. Specifically, the outer list corresponds to
        the grouping methods, of which there can be three at the most, which
        contains a list of groups in the form of lists of site indices. The
        sum of the lengths of the latter must be the same as the total number
        of atoms.
    use_triclinic
        Use format for triclinic cells

    Raises
    ------
    ValueError
        Raised if parameters are incompatible
    """

    # Check velocties parameter
    velocities = structure.get_velocities()
    if velocities is None or np.max(np.abs(velocities)) < 1e-6:
        has_velocity = 0
    else:
        has_velocity = 1

    # Check groupings parameter
    if groupings is None:
        number_of_grouping_methods = 0
    else:
        number_of_grouping_methods = len(groupings)
        if number_of_grouping_methods > 3:
            raise ValueError('There can be no more than 3 grouping methods!')
        for g, grouping in enumerate(groupings):
            all_indices = [i for group in grouping for i in group]
            if len(all_indices) != len(structure) or \
                    set(all_indices) != set(range(len(structure))):
                raise ValueError(f'The indices listed in grouping method {g} are'
                                 ' not compatible with the input'
                                 ' structure!')

    # If not specified, estimate the maximum_neighbors
    if maximum_neighbors is None:
        if cutoff is None:
            cutoff = 0.1
            maximum_neighbors = 1
        else:
            nl = NeighborList([cutoff / 2] * len(structure), skin=2, bothways=True)
            nl.update(structure)
            maximum_neighbors = 0
            for atom in structure:
                maximum_neighbors = max(maximum_neighbors,
                                        len(nl.get_neighbors(atom.index)[0]))
            maximum_neighbors *= 2
            maximum_neighbors = min(maximum_neighbors, 1024)

    # Add header and cell parameters
    lines = []
    if structure.cell.orthorhombic and not use_triclinic:
        triclinic = 0
    else:
        triclinic = 1
    lines.append('{} {} {} {} {} {}'.format(len(structure), maximum_neighbors,
                                            cutoff, triclinic, has_velocity,
                                            number_of_grouping_methods))
    if triclinic:
        lines.append((' {}' * 12)[1:].format(*structure.pbc.astype(int),
                                             *structure.cell[:].flatten()))
    else:
        lines.append((' {}' * 6)[1:].format(*structure.pbc.astype(int),
                                            *structure.cell.lengths()))

    # Add lines for all atoms
    for a, atm in enumerate(structure):
        line = (' {}' * 5)[1:].format(atm.symbol, *atm.position, atm.mass)
        if has_velocity:
            line += (' {}' * 3).format(*velocities[a])
        if groupings is not None:
            for grouping in groupings:
                for i, group in enumerate(grouping):
                    if a in group:
                        line += ' {}'.format(i)
        lines.append(line)

    # Write file
    with open(filename, 'w') as fd:
        fd.write('\n'.join(lines))


# Deprecated! With the `dump_exyz` command one gets `dump.xyz` files
# that contain positions, velocities and forces
# def _generator_vf(fname: str,
#                   n_atoms: int):
#     """
#     Generator for velocity and force data from GPUMD
#     """
#     with open(fname) as f:
#         while True:
#             data = np.loadtxt(f, max_rows=n_atoms, dtype=float)
#             if len(data) == 0:
#                 break
#             yield data


# def convert_gpumd_run_to_traj(dirname: str,
#                               traj_fname: str,
#                               include_velocities: bool = False,
#                               include_forces: bool = False):
#     """Convert a gpumd trajectory (movie.xyz, velocity.out, force.out) to
#     an ASE trajectory file.

#     Parameters
#     ----------
#     dirname
#         gpumd run directory
#     traj_fname
#         output trajectory filename

#     Example
#     -------
#     >>> dirname = 'gpumd-run'
#     >>> traj_fname = 'traj_T100.traj'
#     >>> convert_gpumd_run_to_traj(dirname, traj_fname, include_velocities=True)
#     """

#     # picoseconds to (amu / eV)**0.5 * Ang
#     ps_to_ase = 1e-12 * units.second

#     # setup trajectory file
#     traj = Trajectory(traj_fname, mode='w')

#     # filenames
#     fname_xyz = os.path.join(dirname, 'movie.xyz')
#     fname_v = os.path.join(dirname, 'velocity.out')
#     fname_f = os.path.join(dirname, 'force.out')
#     if not os.path.isfile(fname_xyz):
#         raise ValueError(f'{fname_xyz} does not exist')

#     # read first line to get number of atoms
#     fobj = open(fname_xyz, 'r')
#     n_atoms = int(fobj.readline())
#     print('natoms', n_atoms)
#     fobj.seek(0)

#     # setup generators
#     indices = slice(None, None, 1)
#     gen_xyz = iread_xyz(fobj, indices=indices)
#     gen_v = _generator_vf(fname_v, n_atoms)
#     gen_f = _generator_vf(fname_f, n_atoms)

#     # loop over all snapshots
#     snapshot_index = 0
#     while True:
#         if snapshot_index % 100 == 0:
#             print('  snapshot', snapshot_index)

#         # get xyz
#         try:
#             atoms = next(gen_xyz)
#         except Exception:
#             break
#         assert len(atoms) == n_atoms

#         # get velocities
#         if include_velocities:
#             v = next(gen_v)
#             assert v.shape == (n_atoms, 3), 'Velocities have wrong shape!'
#             atoms.set_velocities(v / ps_to_ase)

#         # get forces
#         if include_forces:
#             f = next(gen_f)
#             assert f.shape == (n_atoms, 3), 'Forces have wrong shape!'
#             calc = SinglePointCalculator(atoms, forces=f)
#             atoms.calc = calc

#         # finalize and write
#         snapshot_index += 1
#         traj.write(atoms)

#     fobj.close()
#     print(f'Converted trajectory of length {snapshot_index}')


# Deprecated! Demonstrate in examples
# def update_database(db_file: str,
#                     runpath: str,
#                     overwrite: bool = False,
#                     ndirs: int = 1,
#                     config_filename: str = 'run.in') -> int:
#     """Parses the runs in the given run directory and compiles the
#     information into an entry of the database. The index of the entry
#     is returned. It is assumed that there is a series of
#     subdirectories in ``runpath``, which each contain a ``kappa.out``
#     or ``hac.out`` and a ``thermo.out`` file. The ``runpath`` should
#     contain a configuration file (``run.in`` or ``config``) and a
#     structure file (``xyz.in``).

#     The last part of the run directory name is used as a unique
#     identifier. If an entry with the name already exists it will be
#     updated. If not a new row is added.

#     Parameters
#     ----------
#     db_file
#         path to database file
#     runpath
#         path to main run directory
#     overwrite
#         if True overwrite ancentry with the same directory name;
#         if False skip the entry
#     ndirs
#         number of directory levels that are used to generate the dirname field
#     config_filename
#         name of configuration; possible values: `run.in`, `config`

#     """
#     dirname = '/'.join(os.path.normpath(runpath).split('/')[-ndirs:])

#     with connect(db_file) as db:
#         try:
#             row = db.get(dirname=dirname)
#             index = row.id
#         except KeyError:
#             index = None
#         if index is not None and not overwrite:
#             print(f'Skipping row {index}; dirname: {dirname}')
#             return

#     # compile information
#     settings = read_settings(os.path.join(runpath, config_filename))
#     structure = read_xyz(os.path.join(runpath, 'xyz.in'))
#     structure.calc = SinglePointCalculator(structure)
#     structure.calc.name = 'gpumd'
#     structure.calc.parameters = settings

#     data = {}

#     kappas = {}
#     for fname in sorted(glob(os.path.join(runpath, '*/kappa.out'))):
#         tag = os.path.dirname(fname).split('/')[-1]
#         kappas[tag] = read_thermo(fname)
#     if len(kappas):
#         data['kappas'] = {key: {col: series.to_numpy() for col, series in df.iteritems()}
#                           for key, df in kappas.items()}

#     hacs = {}
#     for fname in sorted(glob(os.path.join(runpath, '*/hac.out'))):
#         tag = os.path.dirname(fname).split('/')[-1]
#         hacs[tag] = read_thermo(fname)
#     if len(hacs):
#         data['hacs'] = {key: {col: series.to_numpy() for col, series in df.iteritems()}
#                         for key, df in hacs.items()}

#     thermos = {}
#     for fname in sorted(glob(os.path.join(runpath, '*/thermo.out'))):
#         tag = os.path.dirname(fname).split('/')[-1]
#         thermos[tag] = read_thermo(fname)
#     if len(thermos):
#         data['thermos'] = {key: {col: series.to_numpy() for col, series in df.iteritems()}
#                            for key, df in thermos.items()}

#     # compile data that will be stored in fields
#     hostname = socket.gethostname()
#     username = getpass.getuser()
#     information = {'dirname': dirname,
#                    'hostname': hostname,
#                    'username': username,
#                    'data': data,
#                    'n_runs': len(data['thermos'])}
#     for tag in ['temperature', 'Fe_x', 'Fe_y', 'Fe_z', 'fcp_order']:
#         if tag in settings:
#             information[tag] = settings[tag]

#     # add to or update database
#     with connect(db_file) as db:
#         try:
#             row = db.get(dirname=dirname)
#             index = row.id
#         except KeyError:
#             index = None

#         if index is None:
#             print(f'Adding row; dirname: {dirname}')
#             index = db.write(structure, **information)
#         else:
#             print(f'Updating row {index}; dirname: {dirname}')
#             db.update(index, structure, **information)

#     return index


# def read_from_database(row: AtomsRow) -> Tuple[dict, Dict[str, DataFrame], Dict[str, DataFrame]]:
#     """Parses a database entry and returns a tuple comprising the run
#     settings, the thermal conductivity data (from ``kappa.out`` or
#     ``hac.out`` files) and the thermodynamic data (from ``thermo.out`` files).

#     Parameters
#     ----------
#     row
#         row from ASE database

#     """
#     thermos = {}
#     for key, data in row.data['thermos'].items():
#         thermos[key] = DataFrame.from_dict(data)
#         kp_data = {}
#     if 'kappas' in row.data:
#         for key, data in row.data['kappas'].items():
#             kp_data[key] = DataFrame.from_dict(data)
#     elif 'hacs' in row.data:
#         for key, data in row.data['hacs'].items():
#             kp_data[key] = DataFrame.from_dict(data)
#     return row.calculator_parameters, kp_data, thermos
