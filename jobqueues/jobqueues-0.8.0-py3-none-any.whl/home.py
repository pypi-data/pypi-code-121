# (c) 2015-2018 Acellera Ltd http://www.acellera.com
# All Rights Reserved
# Distributed under HTMD Software License Agreement
# No redistribution in whole or part
#
import jobqueues
import os
import sys
import inspect
import platform


def home(dataDir=None, libDir=False):
    """Return the pathname of the root directory (or a data subdirectory).

    Parameters
    ----------
    dataDir : str
        If not None, return the path to a specific data directory
    libDir : bool
        If True, return path to the lib directory

    Returns
    -------
    dir : str
        The directory
    """

    homeDir = os.path.dirname(inspect.getfile(jobqueues))
    try:
        if sys._MEIPASS:
            homeDir = sys._MEIPASS
    except:
        pass

    return homeDir


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    h = home()
    print(h)
