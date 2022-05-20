from typing import List, TextIO
import numpy as np
import sys

if sys.version_info < (3, 9):
    # importlib.resources either doesn't exist or lacks the files()
    # function, so use the PyPI version:
    import importlib_resources
else:
    # importlib.resources has files(), so use that:
    import importlib.resources as importlib_resources

pkg = importlib_resources.files("CLI")
lspath = pkg / 'Latent_spaces'
s_length = pkg / "seq_lengths.csv"


def load_family(fname: str) -> np.ndarray:
    """ Load data from protein family name

    Parameters
    ----------
    fname : str
        Name of protein family

    Returns
    -------
    numpy.ndarray
        The family's latent space data
    """
    try:
        return np.loadtxt(lspath / fname)
    # if a file with that name exists but isn't valid, treat it as a new filename
    except ValueError:
        load_ls_file(fname)


def load_ls_file(fname: str) -> np.ndarray:
    """ Load data from new latent space file

    Parameters
    ----------
    fname : str
        Name of file containing latent space data

    Returns
    -------
    numpy.ndarray
        Latent space data from file
    """
    # try to read the file
    try:
        return np.loadtxt(fname)
    # if it isn't a valid latent space, give an error and quit
    except ValueError:
        print("Invalid file: " + fname)
        print("Files should contain 30 floats, each float in a separate line.")
        exit(2)
    # if the file doesn't exist or can't be read
    except IOError as err:
        exit(err)


def load_sequence(fname: str) -> str:
    """ Load sequence from file

    Parameters
    ----------
    fname : str
        Name of a file containing a new sequence

    Returns
    -------
    str
        New sequence
    """
    try:
        seq_file: TextIO = open(fname, "r+")
        return seq_file.read()
    # if the file doesn't exist or can't be read
    except IOError as err:
        exit(err)


def get_ls_list() -> List[str]:
    """

    Returns
    -------
    List[str]
        List of protein family filenames
    """
    ls_list: List[str] = []
    for f in lspath.iterdir():
        ls_list.append(f.name)
    return ls_list


def is_pf(fname: str) -> bool:
    """ Check if filename is the name of a known protein family

    Parameters
    ----------
    fname : str
        Filename

    Returns
    -------
    bool
    """
    if (lspath / (fname + '.txt')).is_file():
        return True
    return False


latent_space_list: List[str] = get_ls_list()
