#===============================================================================
# PSCAD Annotation Components
#===============================================================================

"""
===========
Annotations
===========
"""

#===============================================================================
# Imports
#===============================================================================

import logging
from typing import Sequence, Union

from mhi.common.arrow import Arrow

from .remote import rmi, rmi_property
from .component import ZComponent, Component
from .component import MovableMixin, SizeableMixin
from .form import FormCodec



#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Codecs
#===============================================================================

_arrow_codec = Arrow()

Directions = Union[int, str, Sequence[str]]


#===============================================================================
# Sticky Note
#===============================================================================

class Sticky(ZComponent, MovableMixin, SizeableMixin):
    """
    A text note which may be placed on a user canvas, and which can have
    arrows pointing in up to 8 directions from the sides/corners of
    the Sticky note.

    .. table:: Sticky Note Parameters

       ============= ====== ===========================================
       Param Name    Type   Description
       ============= ====== ===========================================
       full_font     Font   Font
       align         Choice Alignment: LEFT, CENTRE, RIGHT
       fg_color_adv  Color  Text Colour
       bg_color_adv  Color  Background Colour
       bdr_color_adv Color  Border Colour
       ============= ====== ===========================================
    """

    #---------------------------------------------------------------------------
    # Parameters
    #---------------------------------------------------------------------------

    def _param_codec(self):
        return FormCodec.sticky_note(self)


    text = rmi_property(True, True, doc="Text in the text area", name='text')

    def arrows(self, *args: str, add: Directions = (),
               remove: Directions = ()) -> str:
        """
        Get or set the arrows on the Text Area.

        With no arguments, the current arrows are returned as a string.

        If any positional arguments are given, the arrows are set to the
        indicated directions only.

        If the `add` keyword argument is specified, these arrows
        are added on the text area, joining any existing arrows.

        If the `remove` keyword argument is specified, these arrows
        are removed from the text area.

        The direction arrows may be given as iterable group of strings,
        or as a space-separated string.

        Parameters:
            *args: arrow directions to set on the Text Area
            add: arrow directions to add to the Text Area
            remove: arrow directions to remove from the Text Area

        Returns:
            - a string describing the current arrow configuration

        Examples::

            note.arrows("N", "NE")  # Set North & North-East arrows only.
            note.arrows("N NE")     # Set North & North-East arrows only.
            note.arrows(add="N NE") # Add the North & North-East arrows.
            note.arrows(remove=("N", "NE")) # Remove those arrows.
        """

        if args or add or remove:
            arrows = 0 if args else int(self['arrows'])

            for arg in args:
                arrows |= _arrow_codec.encode(arg)

            arrows |= _arrow_codec.encode(add)
            arrows &= ~_arrow_codec.encode(remove)
            self['arrows'] = arrows
        else:
            arrows = int(self['arrows'])

        return _arrow_codec.decode(arrows)


#===============================================================================
# Divider
#===============================================================================

Weight = Union[str, int, float, None]

class Divider(Component):
    """
    A variable length horizontal or vertical divider that can be added to
    a user canvas.

    .. table:: Divider Settings

       ============== ====== ===================================================
       Param Name     Type   Description
       ============== ====== ===================================================
       state          Choice Display: 2D, 3D
       true-color     Color  Colour
       style          Choice Line Style: SOLID, DASH, DOT, DASHDOT
       weight         Choice Line Weight: 02_PT, 04_PT, 06_PT, 08_PT, 10_PT, \
                             12_PT, 14_PT
       ============== ====== ===================================================
    """


    #---------------------------------------------------------------------------
    # Parameters
    #---------------------------------------------------------------------------

    def _param_codec(self):
        return FormCodec.divider(self)

    @rmi
    def horizontal(self, width: int):
        """
        Set the divider to horizontal orientation with the given width.

        Parameters:
            width (int): the width of the divider, in grid units.
        """

    @rmi
    def vertical(self, height: int):
        """
        Set the divider to vertical orientation with the given height.

        Parameters:
            height (int): the height of the divider, in grid units.
        """

    def flat(self, style: str = None, weight: Weight = None,
             colour: str = None) -> None:
        """
        Set the divider to a non-3D appearence.  Optionally,
        change the line style, weight and colour.

        Parameters:
            style (str): ``SOLID``, ``DASH``, ``DOT``, or ``DASHDOT``. (optional)
            weight: the divider's line weight. (optional)
            colour (str): The divider's line colour. (optional)

        The weight can be given as a floating point number, between 0.2 and 1.4,
        and integer between 0 and 7, or a string such as ``"02_PT"``.
        """

        parameters = dict(state='2D')

        if style:
            parameters['style'] = style

        if weight is not None:
            if isinstance(weight, float):
                if weight < 0.2 or weight > 1.4:
                    raise ValueError("Invalid weight")
                weight = str(int(weight * 5 - 0.5))
            elif isinstance(weight, int):
                if weight < 0 or weight > 7:
                    raise ValueError("Invalid weight")
                weight = str(weight)
            parameters['weight'] = weight

        if colour:
            parameters['true-color'] = colour

        self.parameters(parameters=parameters)

    def solid(self, weight: Weight = None, colour: str = None):
        """
        Set the divider to a non-3D appearence, with a solid line style.
        Optionally, change the line weight and colour.

        Parameters:
            weight: the divider's line weight. (optional)
            colour (str): The divider's line colour. (optional)
        """

        self.flat('SOLID', weight, colour)

    def dashed(self, weight: Weight = None, colour: str = None):
        """
        Set the divider to a non-3D appearence, with a dashed line style.
        Optionally, change the line weight and colour.

        Parameters:
            weight: the divider's line weight. (optional)
            colour (str): The divider's line colour. (optional)
        """

        self.flat('DASH', weight, colour)

    def dotted(self, weight: Weight = None, colour: str = None):
        """
        Set the divider to a non-3D appearence, with a dotted line style.
        Optionally, change the line weight and colour.

        Parameters:
            weight: the divider's line weight. (optional)
            colour (str): The divider's line colour. (optional)
        """

        self.flat('DOT', weight, colour)

    def dot_dash(self, weight: Weight = None, colour: str = None):
        """
        Set the divider to a non-3D appearence, with a dot-dash line style.
        Optionally, change the line weight and colour.

        Parameters:
            weight: the divider's line weight. (optional)
            colour (str): The divider's line colour. (optional)
        """

        self.flat('DASHDOT', weight, colour)

    def raised(self, colour: str = None):
        """
        Set the divider to a 3D appearence.  Optionally, change the colour.

        Parameters:
            colour (str): The divider's line colour. (optional)
        """

        parameters = dict(state='3D')

        if colour:
            parameters['true-color'] = colour

        self.parameters(parameters=parameters)
