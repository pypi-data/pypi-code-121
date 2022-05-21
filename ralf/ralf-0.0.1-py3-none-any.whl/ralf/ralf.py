import math

import scoria
import numpy as np
from scipy.spatial.distance import cdist


def get_rotation_limit(
    pdb_path: str,
    axis_atom_1: int,
    axis_atom_2: int,
    cutoff_distance: float = 1.6,
) -> float:
    """Calculate the maximum rotation for an atropisomer.

    Args:
        pdb_path (str): PDB file for molecule.
        axis_atom_1 (int): ID of first atom bound in chiral axis.
        axis_atom_2 (int): ID of second atom bound in chiral axis.
        cutoff_distance (float, optional): Distance considered overlapping, in angstrom. Defaults to 1.6.

    Returns:
        float: Maximum rotation angle in degrees.
    """
    # python indexing adjustment
    axis_atom_1 -= 1
    axis_atom_2 -= 1

    # output
    maxrotation = 0

    # load the molecule
    mol = scoria.Molecule()
    mol.load_pdb_trajectory_into(
        pdb_path,
        bonds_by_distance=False,
    )

    # get coordinates
    coords = mol.get_coordinates()
    try:
        axisatom1coords = coords[axis_atom_1]
    except IndexError:
        raise RuntimeError(f"Atom ID {axis_atom_1+1} not found for axis_atom_1")
    try:
        axisatom2coords = coords[axis_atom_2]
    except IndexError:
        raise RuntimeError(f"Atom ID {axis_atom_2+1} not found for axis_atom_2")

    if mol.get_bonds()[axis_atom_1][axis_atom_2] == 0:
        raise RuntimeError(f"Atoms {axis_atom_1+1} and {axis_atom_2+1} are not bonded")

    # break central bond
    mol.delete_bond(
        axis_atom_1,
        axis_atom_2,
    )

    # get coords for each half
    nextatoms = mol.select_all_atoms_bound_to_selection(
        np.array([axis_atom_1]),
    )
    tophalfcoords = mol.select_branch(axis_atom_1, nextatoms[0])

    nextatoms = mol.select_all_atoms_bound_to_selection(
        np.array([axis_atom_2]),
    )
    bottomhalfcoords = mol.select_branch(axis_atom_2, nextatoms[0])

    # split molecule into halves
    bottomhalf = mol.get_molecule_from_selection(
        tophalfcoords,
    )

    tophalf = mol.get_molecule_from_selection(
        bottomhalfcoords,
    )

    # save initial orientation
    copy_tophalf = tophalf.copy()

    # rotate in one direction until steric clash
    clash = False
    rot = 0
    while not clash and rot < 180:
        tophalf.rotate_molecule_around_a_line_between_points(
            axisatom1coords,
            axisatom2coords,
            math.radians(1),
        )

        # distance of top half atoms to bottom half
        res = cdist(
            tophalf.get_coordinates(),
            bottomhalf.get_coordinates(),
        )

        # ignore axis atoms
        res[0][0] = np.inf

        # check for close atoms
        clash = np.any(res < cutoff_distance)

        rot += 1

    maxrotation += rot

    # rotate in the other direction until steric clash
    clash = False
    rot = 0
    while not clash and rot > -180:
        copy_tophalf.rotate_molecule_around_a_line_between_points(
            axisatom1coords,
            axisatom2coords,
            math.radians(-1),
        )

        res = cdist(
            copy_tophalf.get_coordinates(),
            bottomhalf.get_coordinates(),
        )

        res[0][0] = np.inf

        clash = np.any(res < cutoff_distance)

        rot -= 1

    maxrotation -= rot

    if maxrotation > 180:
        raise RuntimeError(
            f"""Rotation around indicated bond is unrestricted,
            consider increasing cutoff_distance above {cutoff_distance}."""
        )
    else:
        return maxrotation
