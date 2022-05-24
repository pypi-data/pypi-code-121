#===============================================================================
# PSCAD User Component Definition
#===============================================================================

"""
==========
Definition
==========
"""

#===============================================================================
# Imports
#===============================================================================

import logging
from typing import Dict, Iterable, List, Sequence, Tuple, Union
from xml.etree import ElementTree as ET

from .remote import Remotable, rmi, rmi_property
from .types import View



#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# PSCAD ZComponent
#===============================================================================

class Definition(Remotable):
    """
    Component Definition
    """

    #===========================================================================
    # Properties
    #===========================================================================

    #---------------------------------------------------------------------------
    # Identity
    #---------------------------------------------------------------------------

    @property
    def project_name(self) -> str:
        """
        The project which defines this definition (read-only)
        """
        return self._identity['project']

    @property
    def scope(self) -> str:
        """
        The project which defines this definition (read-only)
        """
        return self.project_name

    @property
    def name(self) -> str:
        """
        Name of the definition
        """
        return self._identity['name']

    @property
    def scoped_name(self) -> str:
        """
        The scoped definition name is the project and definition names,
        separated by a colon.
        """

        return "{}:{}".format(self.project_name, self.name)

    #---------------------------------------------------------------------------
    # XML
    #---------------------------------------------------------------------------

    @rmi_property
    def _xml(self) -> str:
        pass

    @property
    def xml(self):
        """
        XML for the Definition
        """

        return ET.fromstring(self._xml)


    #---------------------------------------------------------------------------
    # Repr
    #---------------------------------------------------------------------------

    def __repr__(self):
        return "Definition[{}]".format(self.scoped_name)


    #===========================================================================
    # Methods
    #===========================================================================

    #---------------------------------------------------------------------------
    # Definition Has a canvas?
    #---------------------------------------------------------------------------

    @rmi
    def is_module(self) -> bool:
        """
        Check to see if this component has its own canvas, with in turn,
        can contain additional components.

        Returns:
            bool: True if the component has an internal canvas, False otherwise.
        """


    #---------------------------------------------------------------------------
    # Definition Compile
    #---------------------------------------------------------------------------

    @rmi
    def _compile(self):
        pass

    def compile(self) -> None:
        """
        Compile this component definition page
        """

        if not self.is_module():
            raise ValueError("Cannot compile; not a module")

        return self._compile()


    #---------------------------------------------------------------------------
    # Navigate Into
    #---------------------------------------------------------------------------

    @rmi
    def navigate_to(self) -> "Canvas":
        """
        Attempt to navigate to the first instance if possible

        Returns:
            Canvas: The definition's canvas
        """

    @rmi
    def _set_view(self, view):
        pass

    def set_view(self, view: Union[str, View]) -> None:
        """
        Activate the appropriate definition editor tab

        Valid view tabs are one of the strings: "Schematic", "Graphic",
        "Parameters", "Script", "Fortran", "Data", or the equivalent
        :class:`.View` constant.

        Parameters:
            view: The desired view tab
        """

        if isinstance(view, str):
            view_id = View[view.upper()].value
        elif isinstance(view, View):
            view_id = view.value
        else:
            raise TypeError("Expected View or View string")

        self._set_view(view_id)


    #---------------------------------------------------------------------------
    # Definition Canvas
    #---------------------------------------------------------------------------

    def canvas(self) -> "Canvas":
        """
        Definition canvas
        """

        prj = self._pscad.project(self.project_name)
        return prj.canvas(self.name)

    @rmi_property
    def _graphics(self):
        pass

    def graphics(self) -> "GfxCanvas":
        """
        Get the :class:`graphics canvas <.GfxCanvas>`

        .. versionadded:: 2.2
        """

        if '_graphic_canvas' not in self.__dict__:
            self._graphic_canvas = self._graphics # pylint: disable=attribute-defined-outside-init

        return self._graphic_canvas


    #---------------------------------------------------------------------------
    # Copy the definition to the clipboard
    #---------------------------------------------------------------------------

    def copy(self) -> None:
        """
        Copy the definition to the clipboard.
        """

        raise NotImplementedError()


    #===========================================================================
    # Scripts, Parameters, ...
    #===========================================================================

    #---------------------------------------------------------------------------
    # Scripts
    #---------------------------------------------------------------------------

    @rmi
    def _script_get(self, section_name):
        pass

    @rmi
    def _script_set(self, section_name):
        pass

    @rmi
    def _script_keys(self):
        pass

    @property
    def script(self):
        """
        The definition's script sections are accessed with this property.

        Examples::

            checks = defn.script['Checks']       # Get script section
            defn.script['Computations'] = "..."  # Add/Change script section
            del defn.script['FlyBy']             # Delete script section

        .. versionadded:: 2.2
        """
        return Scripts(self)


#===============================================================================
# Definition Scripts
#===============================================================================

class Scripts:
    """
    Definition Script Container

    Examples::

        checks = defn.script['Checks']       # Get script section
        defn.script['Computations'] = "..."  # Add/Change script section
        del defn.script['FlyBy']             # Delete script section
    """

    def __init__(self, defn):
        self._defn = defn

    def __getitem__(self, section_name: str) -> str:
        return self._defn._script_get(section_name)

    def __setitem__(self, section_name: str, text: str):
        if not text:
            raise ValueError("Cannot set script section to nothing; "
                             "Try 'del defn.scripts[{!r}]'".format(section_name))
        if not isinstance(text, str):
            raise TypeError("Text section must be a string")

        return self._defn._script_set(section_name, text)

    def __delitem__(self, section_name: str):
        return self._defn._script_set(section_name, None)

    def keys(self) -> Sequence[str]:
        """
        Defined script section names
        """
        return self._defn._script_keys() # pylint: disable=protected-access

    def __iter__(self) -> Iterable[str]:
        return iter(self.keys())


#===============================================================================
# Typing requires complete types at the end of the module
#===============================================================================

# pylint: disable=wrong-import-order, wrong-import-position, ungrouped-imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .canvas import Canvas
    from .graphics import GfxCanvas
