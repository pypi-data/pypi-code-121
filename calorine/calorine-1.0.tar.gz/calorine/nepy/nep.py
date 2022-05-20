import os
import contextlib
import shutil
import tempfile
from typing import List, Tuple
import warnings
import numpy as np
from ase import Atoms
import _nepy


def _create_dummy_nep2(potential_filename: str, symbols: List[str]) -> None:
    """Create a dummy NEP2 model, i.e., a model for which there are no descriptor parameters.
    This is to be used when one wants descriptors not pertaining to a specific NEP3 model.

    Parameters
    ----------
    potential_filename
        Path to which the NEP2 model will be saved.
    symbols
        Atomic elements in the configuration for which to compute descriptors.
    """
    unique_symbols = []
    for sym in symbols:
        if sym not in unique_symbols:
            unique_symbols.append(sym)
    with open(potential_filename, 'w') as f:
        f.write(f'nep {len(unique_symbols)} ')
        for symbol in unique_symbols:
            f.write(f'{symbol} ')
        f.write('\n')
        # Write rest of header
        f.write('cutoff 6 4\nn_max 15 8\nl_max 4\nANN 30 0\n')
        # Write dummy parameters
        # The number of parameters in the network is:
        # N_par = (N_des+2)N_neu + 1 + N_typ**2 (n_max^R + n_max^A + 2)
        # Default settings: 1621 + N_typ**2 * 25
        # The last 52 1:s are the normalization parameters for the descriptors.
        for _ in range(1621 + len(unique_symbols)**2 * 25 + 52):
            f.write(f'  {1e0:e}\n')


def _create_tmp_dir(debug: bool) -> str:
    """Create temporary directory.

    Parameters
    ----------
    debug
        Flag that indicates if debugging. Use a hardcoded path when debugging.

    Returns
    -------
    str
         Path to temporary directory
    """
    if debug:
        tmp_dir = './tmp_nepy/'
        # os.mkdir(tmp_dir)
        try:
            os.mkdir(tmp_dir)
            return tmp_dir
        except FileExistsError:
            raise FileExistsError('Please delete or move the conflicting directory.')
    return tempfile.mkdtemp()


def _clean_tmp_dir(directory: str) -> None:
    """Remove temporary directory.

    Parameters
    ----------
    directory
        Path to temporary directory
    """
    shutil.rmtree(directory)


def _set_default_cell(structure: Atoms, box_length: float = 100):
    """Adds a cubic box to an Atoms object. Atoms object is edited in-place.

    Parameters
    ----------
    structure
        Structure to add box to
    box_length
        Cubic box side length in Å, by default 100
    """
    structure.set_cell([[box_length, 0, 0], [0, box_length, 0], [0, 0, box_length]])
    structure.center()


def get_descriptors(
        structure: Atoms,
        potential_filename: str = None,
        debug: bool = False) -> np.ndarray:
    """Calculates the NEP descriptors for a given structure. A NEP model defined by a nep.txt
    can additionally be provided to get the NEP3 model specific descriptors. If no model is
    provided, a dummy NEP2 model suitable for the provided structure will be created and used.

    Parameters
    ----------
    structure
        Input structure
    potential_filename
        Path to NEP potential. Defaults to None.
    debug
        Flag to toggle debug mode. Makes the generated dummy NEP2 model available
        in a local tmp directory, as well as prints GPUMD output. Defaults to False.

    Returns
    -------
        Descriptors for the supplied structure, with shape (N_atoms, descriptor components)
    """
    local_structure = structure.copy()
    if local_structure.cell.rank == 0:
        warnings.warn('Using default unit cell (box with side 100 Å).')
        _set_default_cell(local_structure)

    N_atoms = len(local_structure)
    c = local_structure.get_cell(complete=True).flatten()
    box = [c[0], c[3], c[6], c[1], c[4], c[7], c[2], c[5], c[8]]

    symbols = local_structure.get_chemical_symbols()
    positions = list(local_structure.get_positions().T.flatten())  # [x1, ..., xN, y1, ... yN,...]

    use_dummy_nep2_potential = potential_filename is None
    if use_dummy_nep2_potential:
        tmp_dir = _create_tmp_dir(debug)
        potential_filename = f'{tmp_dir}/nep.txt'
        _create_dummy_nep2(potential_filename, symbols)

    # Disable output from C++ code by default
    if debug:
        all_descriptors = _nepy.get_descriptors(
            potential_filename, N_atoms, box, symbols, positions)
    else:
        with open(os.devnull, 'w') as f:
            with contextlib.redirect_stdout(f):
                with contextlib.redirect_stderr(f):
                    all_descriptors = _nepy.get_descriptors(
                        potential_filename, N_atoms, box, symbols, positions)

    descriptors_per_atom = np.array(all_descriptors).reshape(-1, N_atoms).T

    if use_dummy_nep2_potential and not debug:
        _clean_tmp_dir(tmp_dir)
    if use_dummy_nep2_potential and debug:
        print(f'DEBUG - Directory containing dummy nep.in: {tmp_dir}')
    return descriptors_per_atom


def get_potential_forces_and_virials(structure: Atoms,
                                     potential_filename: str = None,
                                     debug: bool = False) -> Tuple[np.ndarray]:
    """Calculates the per-atom potential, forces and virials for a given structure.
    A NEP model defined by a nep.txt-file needs to be provided.

    Parameters
    ----------
    structure
        Input structure
    potential_filename
        Path to NEP potential. Defaults to None.
    debug
        Flag to toggle debug mode. Prints GPUMD output. Defaults to False.

    Returns
    -------
        (potential, forces, virials) for the supplied structure,
        with shapes (N_atoms,), (N_atoms,3), (N_atoms,9)
    """
    if potential_filename is None:
        raise ValueError('Potential must be defined!')
    local_structure = structure.copy()
    if local_structure.cell.rank == 0:
        warnings.warn('Using default unit cell (box with side 100 Å).')
        _set_default_cell(local_structure)

    N_atoms = len(local_structure)
    c = local_structure.get_cell(complete=True).flatten()
    box = [c[0], c[3], c[6], c[1], c[4], c[7], c[2], c[5], c[8]]

    symbols = local_structure.get_chemical_symbols()
    positions = list(local_structure.get_positions().T.flatten())  # [x1, ..., xN, y1, ... yN,...]

    # Disable output from C++ code by default
    if debug:
        energies, forces, virials = _nepy.get_potential_forces_and_virials(
            potential_filename, N_atoms, box, symbols, positions)
    else:
        with open(os.devnull, 'w') as f:
            with contextlib.redirect_stdout(f):
                with contextlib.redirect_stderr(f):
                    energies, forces, virials = _nepy.get_potential_forces_and_virials(
                        potential_filename, N_atoms, box, symbols, positions)
    forces_per_atom = np.array(forces).reshape(-1, N_atoms).T
    virials_per_atom = np.array(virials).reshape(-1, N_atoms).T
    return np.array(energies), forces_per_atom, virials_per_atom
