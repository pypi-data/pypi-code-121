from pathlib import Path
import platform
import os
import subprocess
import pkg_resources
import pathlib
import pandas as pd
from subprocess import Popen, PIPE, CalledProcessError
from . import results

"""This file contains internal methods used to run preciso.
"""


def preciso_binary_dir():
    """Returns the path to the folder containing the preciso executable used by `runSimulation()`, as a `pathlib.Path` object.
    """
    return Path(pkg_resources.resource_filename('preciso', 'bin'))

def run_input_file(inputFileName, nodes, n_samples, write_limit=100, debug=False):
    """A tool to run PreciSo with a specified inputFile as input.
    It makes use of a system call to the PreciSo executable. The input file
    should be formatted as described here [1]_.
    PreciSo binaries are treated as package data [2]_ and are therefore accessible using the `pkg_ressources` module.
    System calls are made using `subprocess.getoutput` [3]_.

    .. [1] https://framagit.org/arnall/preciso/wikis/Input%20files%20in%20PreciSo
    .. [2] https://docs.python.org/3/distutils/setupscript.html#installing-package-data
    .. [3] https://docs.python.org/3/library/subprocess.html#subprocess.getoutput

    Parameters
    ----------

    inputFileName : pathlib.Path object or str
        The path to the input file to use in Preciso. Can be given either as
        a `pathlib.Path` object (recommended as it is cross-plateform) or as
        a `str` that complies with the computer's filesystem.
    nodes : List of int (optional)
        The id of the node(s) for which we want the precipitates distribution. Default is [0].
    n_samples: int
        The number of images of the precipitate distribution that should be saved.
    write_limit : int
        The maximum total size of the files written by PreciSo, in Megabytes. It prevents PreciSo from filling up your computer's hard drive. 
        Default value is 100MB. If `write_limit` is of a type different than `int`, no limit is set. **Windows is not supported**, there will be **no limit on this plateform**.
    debug: boolean
        Whether you want to print PreciSo's output directly to the terminal, e.g. to spot situations when it's stuck and can't converge. Default is False.

    Returns
    ----------
    out : Results obj
        The results of the simulation, in the form of a Results object.

    Examples
    --------
    >>> import preciso.run
    >>> preciso.run.run_input_file('')
    Welcome to PreciSo v3.0
    FATAL ERROR: PreciSo have been launch with an incorrect number of arguments

    """
    # Path to the folder in which binaries are stored (preciso/bin)
    binary_folder = preciso_binary_dir()

    if platform.system() == 'Darwin':
        executableFileName = "PreciSo-macOS"
    elif platform.system() == "Linux":
        executableFileName = "PreciSo-linux"
    elif platform.system() == "Windows":
        executableFileName = "PreciSo.exe"
    else:
        raise ValueError(
            "Unable to identify the OS type, found {}.".format(
                platform.system()))

    executable = binary_folder.joinpath(executableFileName)
    if isinstance(write_limit, int) and platform.system() != "Windows":
        prefix = "ulimit -f {};".format(write_limit*1024)
    else:
        prefix = ""
    cmd = """{} {} -file "{}" """.format(prefix, executable, str(inputFileName))

    if debug:
        # This allows to retrieve the stdout live, when preciso is executing
        with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True, shell=True) as p:
            for line in p.stdout:
                print(line, end='')  # process line here
            p.wait()
            out = p.stdout
            exitcode = p.returncode
    else:
        exitcode, out = subprocess.getstatusoutput(cmd)

    if exitcode == 0:
        simulation_result = results.Results(inputFileName, os.getcwd(), out, nodes, n_samples)
        return simulation_result
    else:
        raise RuntimeError('PreciSo failed with exitcode {}, stdout :\n{}'.format(exitcode, out))

