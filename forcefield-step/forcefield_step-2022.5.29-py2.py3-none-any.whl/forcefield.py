# -*- coding: utf-8 -*-

"""A node or step for the forcefield in a flowchart"""

import logging
import os.path
import pkg_resources
import pprint

import forcefield_step
import seamm_ff_util
import seamm
import seamm_util.printing as printing
from seamm_util.printing import FormattedText as __

logger = logging.getLogger(__name__)
# logger.setLevel("DEBUG")
job = printing.getPrinter()
printer = printing.getPrinter("forcefield")


class Forcefield(seamm.Node):
    def __init__(self, flowchart=None, extension=None):
        """Initialize a forcefield step

        Keyword arguments:
        """
        logger.debug("Creating Forcefield {}".format(self))

        super().__init__(flowchart=flowchart, title="Forcefield", extension=extension)

        self.parameters = forcefield_step.ForcefieldParameters()

    @property
    def version(self):
        """The semantic version of this module."""
        return forcefield_step.__version__

    @property
    def git_revision(self):
        """The git version of this module."""
        return forcefield_step.__git_revision__

    def description_text(self, P=None):
        """Return a short description of this step.

        Return a nicely formatted string describing what this step will
        do.

        Keyword arguments:
            P: a dictionary of parameter values, which may be variables
                or final values. If None, then the parameters values will
                be used as is.
        """

        if not P:
            P = self.parameters.values_to_dict()

        if P["task"] == "setup forcefield":
            if P["forcefield_file"][0] == "$":
                text = (
                    "Read the forcefield file given in the variable"
                    " '{forcefield_file}' and use the {forcefield} "
                    "forcefield."
                )
            elif P["forcefield_file"] == "OpenKIM":
                text = "Use the OpenKIM potential '{potentials}'"
            else:
                text = (
                    "Read the forcefield file '{forcefield_file}' "
                    "and use the {forcefield} forcefield."
                )
        elif P["task"] == "assign forcefield to structure":
            text = "Assign the atom types to the structure."

        return (
            self.header
            + "\n"
            + __(
                text,
                indent=4 * " ",
                **P,
            ).__str__()
        )

    def run(self):
        """Setup the forcefield"""

        next_node = super().run(printer=printer)

        P = self.parameters.current_values_to_dict(
            context=seamm.flowchart_variables._data
        )

        printer.important(__(self.header, indent=self.indent))

        if P["task"] == "setup forcefield":
            self.setup_forcefield(P)
        elif P["task"] == "assign forcefield to structure":
            self.assign_forcefield(P)

        printer.important("")

        return next_node

    def assign_forcefield(self, P=None):
        """Assign the forcefield to the structure, i.e. find the atom types
        and charges.

        Parameters
        ----------
        P : {str: Any}
            The final values of the parameters.

        Returns
        -------
        None
        """
        # if P is None:
        #     P = self.parameters.current_values_to_dict(
        #         context=seamm.flowchart_variables._data
        #     )

        ff = self.get_variable("_forcefield")
        system_db = self.get_variable("_system_db")
        configuration = system_db.system.configuration

        ffname = ff.current_forcefield
        printer.important(
            __(
                "Assigning the atom types and charges for forcefield "
                f"'{ffname}' to the system",
                indent=self.indent + "    ",
            )
        )

        # Atom types
        logger.debug("Atom typing, getting the SMILES for the system")
        smiles = configuration.to_smiles(hydrogens=True)
        logger.debug("Atom typing -- smiles = " + smiles)
        ff_assigner = seamm_ff_util.FFAssigner(ff)
        atom_types = ff_assigner.assign(configuration)
        logger.info("Atom types: " + ", ".join(atom_types))
        key = f"atom_types_{ffname}"
        if key not in configuration.atoms:
            configuration.atoms.add_attribute(key, coltype="str")
        configuration.atoms[key] = atom_types

        # Now get the charges if forcefield has them.
        terms = ff.data["forcefield"][ffname]["parameters"]
        if "bond_increments" in terms:
            logger.debug("Getting the charges for the system")
            neighbors = configuration.bonded_neighbors(as_indices=True)

            logger.debug(f"{atom_types=}")
            logger.debug(f"{neighbors=}")

            charges = []
            total_q = 0.0
            for i in range(configuration.n_atoms):
                itype = atom_types[i]
                parameters = ff.charges(itype)[3]
                q = float(parameters["Q"])
                for j in neighbors[i]:
                    jtype = atom_types[j]
                    parameters = ff.bond_increments(itype, jtype)[3]
                    q += float(parameters["deltaij"])
                charges.append(q)
                total_q += q
            if abs(total_q) > 0.0001:
                logger.warning("Total charge is not zero: {}".format(total_q))
                logger.info(
                    "Charges from increments and charges:\n" + pprint.pformat(charges)
                )
            else:
                logger.debug("Charges from increments:\n" + pprint.pformat(charges))

            key = f"charges_{ffname}"
            if key not in configuration.atoms:
                configuration.atoms.add_attribute(key, coltype="float")
            charge_column = configuration.atoms.get_column(key)
            charge_column[0:] = charges
            logger.debug(f"Set column '{key}' to the charges")

            printer.important(
                __(
                    "Assigned atom types and charges to "
                    f"{configuration.n_atoms} atoms.",
                    indent=self.indent + "    ",
                )
            )
        else:
            printer.important(
                __(
                    f"Assigned atom types to {configuration.n_atoms} " "atoms.",
                    indent=self.indent + "    ",
                )
            )

    def setup_forcefield(self, P=None):
        """Setup the forcefield for later use.

        Parameters
        ---------
        P : {str: Any}
            The final values of the parameters.

        Returns
        -------
        None
        """
        if P is None:
            P = self.parameters.current_values_to_dict(
                context=seamm.flowchart_variables._data
            )

        if P["forcefield_file"] == "OpenKIM":
            printer.important(
                __(
                    "Using the OpenKIM potential '{potentials}'",
                    **P,
                    indent=self.indent + "    ",
                )
            )
            self.set_variable("_forcefield", "OpenKIM")
            self.set_variable("_OpenKIM_Potential", P["potentials"])
        else:
            printer.important(
                __(
                    "Reading the forcefield file '{forcefield_file}'",
                    **P,
                    indent=self.indent + "    ",
                )
            )

            # Find the forcefield file
            path = pkg_resources.resource_filename(__name__, "data/")
            ff_file = os.path.join(path, P["forcefield_file"])

            ff = seamm_ff_util.Forcefield(ff_file)
            self.set_variable("_forcefield", ff)

            if P["forcefield"] == "default":
                printer.important(
                    __(
                        "   Using the default forcefield '{ff}'.",
                        ff=ff.forcefields[0],
                        indent=self.indent + "    ",
                    )
                )

                ff.initialize_biosym_forcefield()
            else:
                printer.important(
                    __(
                        "   Using the forcefield '{forcefield}'",
                        **P,
                        indent=self.indent + "    ",
                    )
                )

                ff.initialize_biosym_forcefield(P["forcefield"])
