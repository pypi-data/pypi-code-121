"""
The public interface to the read_structure_step SEAMM plugin
"""

from . import formats
import os


def write(
    file_name,
    configurations,
    extension=None,
    remove_hydrogens="no",
    printer=None,
    references=None,
    bibliography=None,
):
    """
    Calls the appropriate functions to parse the requested file.

    Parameters
    ----------
    file_name : str
        Name of the file

    configurations : [Configuration]
        The SEAMM configuration(s) to write

    extension : str, optional, default: None
        The extension, including initial dot, defining the format.

    remove_hydrogens : str = "no"
        Whether to remove hydrogen atoms before writing the structure to file.

    printer : Logger or Printer
        A function that prints to the appropriate place, used for progress.

    references : ReferenceHandler = None
        The reference handler object or None

    bibliography : dict
        The bibliography as a dictionary.
        The list of configurations created.
    """

    if type(file_name) is not str:
        raise TypeError(
            """write_structure_step: The file name must be a string, but a
            %s was given. """
            % str(type(file_name))
        )

    if file_name == "":
        raise NameError(
            """write_structure_step: The file name for the structure file
            was not specified."""
        )

    file_name = os.path.abspath(file_name)

    if extension is None:
        raise NameError("Extension could not be identified")

    if extension not in formats.registries.REGISTERED_WRITERS.keys():
        raise KeyError(
            "write_structure_step: the file format %s was not recognized." % extension
        )

    writer = formats.registries.REGISTERED_WRITERS[extension]["function"]

    writer(
        file_name,
        configurations,
        extension=extension,
        remove_hydrogens=remove_hydrogens,
        printer=printer,
        references=references,
        bibliography=bibliography,
    )
