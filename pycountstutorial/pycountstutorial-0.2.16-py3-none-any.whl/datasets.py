from importlib import resources


def get_flatland_path():
    """Get path to example "Flatland" [1]_ text file.

    Returns
    -------
    pathlib.Path
        Path to file.

    References
    ----------
    .. [1] E. A. Abbott, "Flatland", Seeley & Co., 1884.
    """
    with resources.path("pycountstutorial.data", "flatland.txt") as p:
        data_file_path = p
    return data_file_path


def get_einstein_path():
    """Get path to example "Einstein quote" text file.

    Returns
    -------
    pathlib.Path
        Path to file.
    """
    with resources.path("pycountstutorial.data", "einstein.txt") as p:
        data_file_path = p
    return data_file_path


def get_zen_path():
    """Get path to example "The Zen of Python" [1]_ text file.

    Returns
    -------
    pathlib.Path
        Path to file.

    References
    ----------
    .. [1] https://peps.python.org/pep-0020/
    """
    with resources.path("pycountstutorial.data", "zen.txt") as p:
        data_file_path = p
    return data_file_path
