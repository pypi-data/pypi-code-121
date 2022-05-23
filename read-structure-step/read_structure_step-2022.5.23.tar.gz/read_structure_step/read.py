"""
The public interface to the read_structure_step SEAMM plugin
"""

from . import utils
from . import formats
import os


def read(
    file_name,
    configuration,
    extension=None,
    add_hydrogens=False,
    system_db=None,
    system=None,
    indices=None,
    subsequent_as_configurations=False,
    system_name=None,
    configuration_name=None,
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

    configuration : Configuration
        The SEAMM configuration to read into

    extension : str, optional, default: None
        The extension, including initial dot, defining the format.

    add_hydrogens : bool = False
        Whether to add any missing hydrogen atoms.

    system_db : System_DB = None
        The system database, used if multiple structures in the file.

    system : System = None
        The system to use if adding subsequent structures as configurations.

    indices : str = None
        The generalized indices (slices, SMARTS, etc.) to select structures
        from a file containing multiple structures.

    subsequent_as_configurations : bool = False
        Normally and subsequent structures are loaded into new systems; however,
        if this option is True, they will be added as configurations.

    system_name : str = None
        The name for systems. Can be directives like "SMILES" or
        "Canonical SMILES". If None, no name is given.

    configuration_name : str = None
        The name for configurations. Can be directives like "SMILES" or
        "Canonical SMILES". If None, no name is given.

    printer : Logger or Printer
        A function that prints to the appropriate place, used for progress.

    references : ReferenceHandler = None
        The reference handler object or None

    bibliography : dict
        The bibliography as a dictionary.

    Returns
    -------
    [Configuration]
        The list of configurations created.
    """

    if type(file_name) is not str:
        raise TypeError(
            """read_structure_step: The file name must be a string, but a
            %s was given. """
            % str(type(file_name))
        )

    if file_name == "":
        raise NameError(
            """read_structure_step: The file name for the structure file
            was not specified."""
        )

    file_name = os.path.abspath(file_name)

    if extension is None:

        extension = utils.guess_extension(file_name, use_file_name=True)

        if extension is None:

            extension = utils.guess_extension(file_name, use_file_name=False)

    else:
        extension = utils.sanitize_file_format(extension)

    if extension is None:
        raise NameError("Extension could not be identified")

    if extension not in formats.registries.REGISTERED_READERS.keys():
        raise KeyError(
            "read_structure_step: the file format %s was not recognized." % extension
        )

    reader = formats.registries.REGISTERED_READERS[extension]["function"]

    configurations = reader(
        file_name,
        configuration,
        extension=extension,
        add_hydrogens=add_hydrogens,
        system_db=system_db,
        system=system,
        indices=indices,
        subsequent_as_configurations=subsequent_as_configurations,
        system_name=system_name,
        configuration_name=configuration_name,
        printer=printer,
        references=references,
        bibliography=bibliography,
    )

    return configurations
