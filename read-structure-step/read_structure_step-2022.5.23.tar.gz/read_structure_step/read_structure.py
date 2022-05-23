# -*- coding: utf-8 -*-

"""Non-graphical part of the Read Structure step in a SEAMM flowchart

In addition to the normal logger, two logger-like printing facilities are
defined: 'job' and 'printer'. 'job' send output to the main job.out file for
the job, and should be used very sparingly, typically to echo what this step
will do in the initial summary of the job.

'printer' sends output to the file 'step.out' in this steps working
directory, and is used for all normal output from this step.
"""

import logging
from pathlib import PurePath, Path
import tarfile
import tempfile
import textwrap

from .formats.registries import get_format_metadata
import read_structure_step
from .read import read
import seamm
from seamm_util import ureg, Q_  # noqa: F401
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __
from .utils import guess_extension

logger = logging.getLogger(__name__)
job = printing.getPrinter()
printer = printing.getPrinter("Read Structure")


class ReadStructure(seamm.Node):
    def __init__(self, flowchart=None, title="Read Structure", extension=None):
        """A step for Read Structure in a SEAMM flowchart.

        You may wish to change the title above, which is the string displayed
        in the box representing the step in the flowchart.

        Parameters:
            flowchart: The flowchart that contains this step.
            title: The name displayed in the flowchart.

            extension: ??

        Returns:
            None
        """
        logger.debug("Creating Read Structure {}".format(self))

        # Set the logging level for this module if requested
        # if 'read_structure_step_log_level' in self.options:
        #     logger.setLevel(self.options.read_structure_step_log_level)

        super().__init__(
            flowchart=flowchart, title=title, extension=extension, logger=logger
        )  # yapf: disable

        self.parameters = read_structure_step.ReadStructureParameters()

    @property
    def version(self):
        """The semantic version of this module."""
        return read_structure_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return read_structure_step.__git_revision__

    def description_text(self, P=None):
        """Create the text description of what this step will do.
        The dictionary of control values is passed in as P so that
        the code can test values, etc.

        Keyword arguments:
            P: An optional dictionary of the current values of the control
               parameters.
        """

        if not P:
            P = self.parameters.values_to_dict()

        text = f"Read structure from {P['file']}. "

        # What type of file?
        extension = ""
        if isinstance(P["file"], Path):
            filename = str(P["file"])
        else:
            filename = P["file"].strip()
        file_type = P["file type"]

        if self.is_expr(filename) or self.is_expr(file_type):
            extension = "all"
        else:
            if file_type != "from extension":
                extension = file_type.split()[0]
            else:
                if filename != "":
                    path = PurePath(filename)
                    extension = path.suffix
                    if extension == ".gz":
                        extension = path.stem.suffix

        # Get the metadata for the format
        metadata = get_format_metadata(extension)

        if extension == "all" or not metadata["single_structure"]:
            text += seamm.standard_parameters.multiple_structure_handling_description(P)
        else:
            text += seamm.standard_parameters.structure_handling_description(P)

        text = textwrap.fill(text, initial_indent=4 * " ", subsequent_indent=4 * " ")
        return self.header + "\n" + text

    def run(self):
        """Run a Read Structure step."""
        next_node = super().run(printer)

        # Get the values of the parameters, dereferencing any variables
        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        # Check for tar files, potentially compressed
        if isinstance(P["file"], Path):
            path = P["file"]
        else:
            path = Path(["file"].strip())

        extensions = path.suffixes
        if ".tar" in extensions or ".tgz" in extensions:
            self.read_tarfile(path, P)
        else:
            # What type of file?
            if isinstance(P["file"], Path):
                filename = str(P["file"])
            else:
                filename = ["file"].strip()
            file_type = P["file type"]

            if file_type != "from extension":
                extension = file_type.split()[0]
            else:
                path = PurePath(filename)
                extension = path.suffix
                if extension == ".gz":
                    extension = path.stem.suffix

            if extension == "":
                extension = guess_extension(filename, use_file_name=False)
                P["file type"] = extension

            # Print what we are doing
            printer.important(self.description_text(P))

            # Read the file into the system
            system_db = self.get_variable("_system_db")
            system, configuration = self.get_system_configuration(
                P, structure_handling=True
            )

            read(
                filename,
                configuration,
                extension=extension,
                add_hydrogens=P["add hydrogens"],
                system_db=system_db,
                system=system,
                indices=P["indices"],
                subsequent_as_configurations=(
                    P["subsequent structure handling"] == "Create a new configuration"
                ),
                system_name=P["system name"],
                configuration_name=P["configuration name"],
                printer=printer.important,
                references=self.references,
                bibliography=self._bibliography,
            )

            # Finish the output
            system, configuration = self.get_system_configuration(
                P, structure_handling=False
            )
            if configuration.periodicity == 3:
                space_group = configuration.symmetry.group
                if space_group == "":
                    symmetry_info = ""
                else:
                    symmetry_info = f" The space group is {space_group}."
                printer.important(
                    __(
                        "\n    Created a periodic structure with "
                        f"{configuration.n_atoms} atoms. {symmetry_info}"
                        f"\n           System name = {system.name}"
                        f"\n    Configuration name = {configuration.name}",
                        indent=4 * " ",
                    )
                )
            else:
                printer.important(
                    __(
                        "\n    Created a molecular structure with "
                        f"{configuration.n_atoms} atoms."
                        f"\n           System name = {system.name}"
                        f"\n    Configuration name = {configuration.name}",
                        indent=4 * " ",
                    )
                )

        printer.important("")

        return next_node

    def read_tarfile(self, tarfile_path, P):
        """Read structures from a tarfile.

        Parameters
        ----------
        path : pathlib.Path
            The path to the tarfile.
        P : {str: str}
            Dictionary of control parameters for this step.
        """
        file_type = P["file type"]
        if file_type != "from extension":
            extensions = [file_type.split()[0]]

        as_configurations = (
            P["subsequent structure handling"] == "Create a new configuration"
        )

        n = 0
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_dir_path = Path(tmp_dir)
            with tarfile.open(tarfile_path.expanduser(), "r") as tar:
                for member in tar:
                    if not member.isfile():
                        continue

                    if member.name[0] == ".":
                        continue

                    path = PurePath(member.name)
                    if path.name[0] == ".":
                        continue
                    extension = path.suffix

                    # If explicit extension does not match, skip.
                    if file_type != "from extension" and extension not in extensions:
                        continue

                    # For the time being write the contents to a file. Eventually should
                    # rewrite all the routines to handle text as well as files.
                    fd = tar.extractfile(member)
                    if fd is None:
                        fd.close()
                        continue

                    data = fd.read()
                    fd.close()

                    tmp_path = tmp_dir_path / path.name
                    tmp_path.write_bytes(data)

                    filename = str(tmp_path)

                    if extension == "":
                        extension = guess_extension(filename)

                    # Read the file into the system
                    system_db = self.get_variable("_system_db")
                    system, configuration = self.get_system_configuration(
                        P, structure_handling=True
                    )

                    read(
                        filename,
                        configuration,
                        extension=extension,
                        add_hydrogens=P["add hydrogens"],
                        system_db=system_db,
                        system=system,
                        indices=P["indices"],
                        subsequent_as_configurations=as_configurations,
                        system_name=P["system name"],
                        configuration_name=P["configuration name"],
                        printer=printer.important,
                        references=self.references,
                        bibliography=self._bibliography,
                    )

                    tmp_path.unlink()
                    n += 1
                    if n % 1000 == 0:
                        print(n)

        printer.important(
            __(
                f"\n    Created {n} structures from the tarfile {tarfile}",
                indent=4 * " ",
            )
        )
