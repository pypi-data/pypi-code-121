"""
The mmcif reader/writer
"""

import logging
from pathlib import Path

from ..registries import register_format_checker
from ..registries import register_reader
from ..registries import set_format_metadata

logger = logging.getLogger(__name__)

set_format_metadata(
    [".mmcif"],
    single_structure=False,
    dimensionality=3,
    coordinate_dimensionality=3,
    property_data=True,
    bonds=True,
    is_complete=True,
    add_hydrogens=False,
)


@register_format_checker(".mmcif")
def check_format(path):
    """Check if a file is a Macromolecular Crystallographic Information File (mmCIF)
    file

    Check for "data_..." at the beginning of a line and dots in item keys

    Parameters
    ----------
    path : str or Path
    """
    result = False
    in_data_block = False
    with open(path, "r") as fd:
        for line in fd:
            line = line.strip()
            if in_data_block:
                if line[0] == "_":
                    result = "." in line.split()[0]
                    break
            if line[0:5] == "data_":
                in_data_block = True
    return result


@register_reader(".mmcif -- Macromolecular Crystallographic Information File")
def load_mmcif(
    path,
    configuration,
    extension=".mmcif",
    add_hydrogens=False,
    system_db=None,
    system=None,
    indices="1:end",
    subsequent_as_configurations=False,
    system_name="from file",
    configuration_name="sequential",
    printer=None,
    references=None,
    bibliography=None,
    **kwargs,
):
    """Read a Macromolecular Crystallographic Information File

    See https://mmcif.wwpdb.org/pdbx-mmcif-home-page.html for a description
    of the format.

    Parameters
    ----------
    file_name : str or Path
        The path to the file, as either a string or Path.

    configuration : molsystem.Configuration
        The configuration to put the imported structure into.

    extension : str, optional, default: None
        The extension, including initial dot, defining the format.

    add_hydrogens : bool = False
        Whether to add any missing hydrogen atoms.

    system_db : System_DB = None
        The system database, used if multiple structures in the file.

    system : System = None
        The system to use if adding subsequent structures as configurations.

    indices : str = "1:end"
        The generalized indices (slices, SMARTS, etc.) to select structures
        from a file containing multiple structures.

    subsequent_as_configurations : bool = False
        Normally and subsequent structures are loaded into new systems; however,
        if this option is True, they will be added as configurations.

    system_name : str = "from file"
        The name for systems. Can be directives like "SMILES" or
        "Canonical SMILES". If None, no name is given.

    configuration_name : str = "sequential"
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
    if isinstance(path, str):
        path = Path(path)

    path.expanduser().resolve()

    structure_no = 0
    lines = []
    in_block = False
    block_name = ""
    with open(path, "r") as fd:
        for line in fd:
            if line[0:5] == "data_":
                logger.debug(f"Found block {line}")
                if not in_block:
                    in_block = True
                    block_name = line[5:].strip()
                else:
                    structure_no += 1
                    # Check for NMR ensemble
                    text = "\n".join(lines)
                    if "_pdbx_nmr_ensemble.conformers_submitted_total_number" in text:
                        system = system_db.create_system()
                        system.from_mmcif_text(text)
                    else:
                        if structure_no > 1:
                            if subsequent_as_configurations:
                                configuration = system.create_configuration()
                            else:
                                system = system_db.create_system()
                                configuration = system.create_configuration()

                        configuration.from_mmcif_text(text)

                    logger.debug(f"   added system {system_db.n_systems}: {block_name}")

                    # Set the system name
                    if system_name is not None and system_name != "":
                        lower_name = str(system_name).lower()
                        if "from file" in lower_name:
                            system.name = block_name
                        elif "file name" in lower_name:
                            system.name = path.stem
                        elif "formula" in lower_name:
                            system.name = configuration.formula()[0]
                        elif "empirical formula" in lower_name:
                            system.name = configuration.formula()[1]
                        else:
                            system.name = str(system_name)

                    # And the configuration name
                    if configuration_name is not None and configuration_name != "":
                        lower_name = str(configuration_name).lower()
                        if "from file" in lower_name:
                            configuration.name = block_name
                        elif "file name" in lower_name:
                            configuration.name = path.stem
                        elif "formula" in lower_name:
                            configuration.name = configuration.formula()[0]
                        elif "empirical formula" in lower_name:
                            configuration.name = configuration.formula()[1]
                        else:
                            configuration.name = str(configuration_name)
                    logger.debug(f"   added system {system_db.n_systems}: {block_name}")
                block_name = line[5:].strip()
                lines = []
            lines.append(line)

        if len(lines) > 0:
            # The last block just ends at the end of the file
            structure_no += 1
            # Check for NMR ensemble
            text = "\n".join(lines)
            if "_pdbx_nmr_ensemble.conformers_submitted_total_number" in text:
                system = system_db.create_system()
                system.from_mmcif_text(text)
            else:
                if structure_no > 1:
                    if subsequent_as_configurations:
                        configuration = system.create_configuration()
                    else:
                        system = system_db.create_system()
                        configuration = system.create_configuration()

                configuration.from_mmcif_text(text)

            logger.debug(f"   added system {system_db.n_systems}: {block_name}")

            # Set the system name
            if system_name is not None and system_name != "":
                lower_name = str(system_name).lower()
                if "from file" in lower_name:
                    system.name = block_name
                elif "file name" in lower_name:
                    system.name = path.stem
                elif "formula" in lower_name:
                    system.name = configuration.formula()[0]
                elif "empirical formula" in lower_name:
                    system.name = configuration.formula()[1]
                else:
                    system.name = str(system_name)

            # And the configuration name
            if configuration_name is not None and configuration_name != "":
                lower_name = str(configuration_name).lower()
                if "from file" in lower_name:
                    configuration.name = block_name
                elif "file name" in lower_name:
                    configuration.name = path.stem
                elif "formula" in lower_name:
                    configuration.name = configuration.formula()[0]
                elif "empirical formula" in lower_name:
                    configuration.name = configuration.formula()[1]
                else:
                    configuration.name = str(configuration_name)
