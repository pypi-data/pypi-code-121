"""
Errors for the various modules in the plugin
"""


class Error(Exception):
    """Base class for exceptions raised by the read_structure_step"""

    pass


class Mol2Error(Error):
    """Class for exceptions raised by the Mol2 module in
    read_structure_step"""

    pass


class XYZError(Error):
    """Class for exceptions raised by the XYZ module in read_structure_step"""

    pass


class PDBError(Error):
    """Class for exceptions raised by the PDB module in read_structure_step"""

    pass


class SDFError(Error):
    """Class for exceptions raised by the SDF module in read_structure_step"""

    pass


class MopError(Error):
    """Class for exceptions raised by the MOPAC module in
    read_structure_step"""

    pass
