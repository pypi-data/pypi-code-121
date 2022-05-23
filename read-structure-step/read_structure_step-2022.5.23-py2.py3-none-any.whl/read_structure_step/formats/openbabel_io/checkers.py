import re

from read_structure_step.formats.registries import last_resort_checker


def check_for_pdb(file_name):
    """Check if a file appears to be a PDB file.

    The PDB files have a number of required keywords; however, some, like "AUTHOR"
    are common words, so this routine checks for the simultaneous presence of a
    number of the strangely spelled keywords.

    Parameters
    ----------
    file_name : str
        The path to the file.

    Returns
    -------
    bool
        True if the file appears to be a PDB file.
    """
    keywords = (
        "COMPND",
        "KEYWDS",
        "EXPDTA",
        "REVDAT",
        "REMARK 2",
        "REMARK 3",
        "SEQRES",
        "CRYST1",
    )

    with open(file_name, "r") as f:
        data = f.read()

    if all(keyword in data for keyword in keywords):
        return True
    else:
        return False


def check_for_xyz(file_name):
    """Check if a file appears to be an XYZ file.

    Parameters
    ----------
    file_name : str
        The path to the file.

    Returns
    -------
    bool
        True if the file appears to be a PDB file.
    """
    element_coords_regex = r"""^\s*(A[cglmrstu]|B[aehikr]?|C[adeflmnorsu] \
            ?|D[bsy]|E[rsu]|F[elmr]?|G[ade]|H[efgos]?|I[nr]?|Kr?|L[airuv] \
            |M[dgnot]|N[abdeiop]?|Os?|P[abdmortu]?|R[abefghnu]|S[bcegimnr\]?| \
            T[abcehilm]|U(u[opst])?|V|W|Xe|Yb?|Z[nr \
            ])\s*(\s*-?\d+(\.\d+([-+]e\d+)?)?\s*){3}$"""

    with open(file_name, "r") as f:
        for line_nbr, line in enumerate(f):
            if line_nbr > 2:
                break

            if line_nbr == 0 and re.search(r"^\s*[0-9]+\s*$", line) is None:
                return False

            if line_nbr == 2 and re.search(element_coords_regex, line) is not None:
                return True

    return False


def add_format_checkers():
    """Add any missing format checkers."""
    last_resort_checker(".pdb", check_for_pdb)
    last_resort_checker(".xyz", check_for_xyz)
