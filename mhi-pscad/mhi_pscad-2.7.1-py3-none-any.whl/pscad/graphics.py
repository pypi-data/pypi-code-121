#===============================================================================
# PSCAD Graphics Components
#===============================================================================

"""
===================
Graphics Components
===================

.. versionadded:: 2.2
"""

#===============================================================================
# Imports
#===============================================================================

import logging
from typing import Tuple, Optional
from enum import Enum

from .remote import rmi, rmi_property
from .component import ZComponent, MovableMixin, SizeableMixin, Point
from .canvas import Canvas
from .form import FormCodec


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# Graphic Object Identifiers
#===============================================================================

class Gfx(Enum):
    """
    Enumeration constants, representing various graphical shapes

    .. versionadded:: 2.2
    """

    # Standard Types
    Line = (0, )
    Rect = (1, )
    Oval = (2, )
    Arc = (3, )
    Text = (4, )
    Node = (5, )
    Shape = (6, )

    # Shape subtypes
    Bezier = (6, 0)
    RectRound = (6, 1)
    TriangleRight = (6, 2)
    TriangleIso = (6, 3)
    Diamond = (6, 4)
    Parallelogram = (6, 5)
    Trapezoid = (6, 6)
    Pentagon = (6, 7)
    Hexagon = (6, 8)
    ArrowUp = (6, 9)
    ArrowRight = (6, 10)
    ArrowDown = (6, 11)
    ArrowLeft = (6, 12)
    Star4 = (6, 13)
    Star5 = (6, 14)
    Star6 = (6, 15)
    SpeachRect = (6, 16)
    SpeachOval = (6, 17)
    Heart = (6, 18)
    Lightning = (6, 19)
    Constant = (6, 20)


#===============================================================================
# PSCAD Graphic Canvas
#===============================================================================

class GfxCanvas(Canvas):

    """
    A graphics canvas is a surface where graphic components can be placed and
    arranged.

    The graphic canvas is accessed with
    :meth:`defn.graphics <.Definition.graphics>`.

    .. versionadded:: 2.2
    """

    @rmi
    def _create(self, shape, extra):          # pylint: disable=arguments-differ
        pass

    def create_component(self, shape: Gfx, extra=None): # type: ignore
        """
        Create a new graphic object on a Graphics canvas.
        """

        if not isinstance(shape, Gfx):
            raise TypeError("shape must be a Gfx enum")
        if extra is None and len(shape.value) == 2:
            shape, extra = Gfx.Shape, shape

        if shape == Gfx.Arc:
            if not isinstance(extra, int):
                raise TypeError("Arc must be given an integer angle")
        elif shape == Gfx.Shape:
            if isinstance(extra, Gfx) and len(extra.value) == 2:
                extra = extra.value[1]
            else:
                raise TypeError("Invalid Gfx.Shape parameter")
        elif extra is not None:
            raise TypeError("Unexpected argument")
        else:
            extra = 0

        return self._create(shape.value[0], extra)


    #---------------------------------------------------------------------------
    # Component wizard add methods
    #---------------------------------------------------------------------------

    def add_port(self, location, name: str, mode: str, *, dim: int = 1,
                 **kwargs):
        """
        Add a port to the component definition.
        """

        port = self.create_component(Gfx.Node)
        port.location = location
        port.parameters(name=name, mode=mode, dim=dim, **kwargs)
        return port

    def add_input(self, location, name: str, dim: int = 1,
                  datatype: str = 'REAL'):
        """
        Add a control signal input port to the component definition.
        """

        port = self.add_port(location, name, 'CONTROL_SIGNAL_INPUT', dim=dim,
                             datatype=datatype)
        return port

    def add_output(self, location, name: str, dim: int = 1,
                   datatype: str = 'REAL'):
        """
        Add a control signal output port to the component definition.
        """

        port = self.add_port(location, name, 'CONTROL_SIGNAL_INPUT', dim=dim,
                             datatype=datatype)
        return port

    def add_electrical(self, location, name: str, dim: int = 1,
                       electype: str = 'FIXED'):
        """
        Add an electrical connection port to the component definition.
        """

        port = self.add_port(location, name, 'ELECTRICAL_NODE', dim=dim,
                             electype=electype)
        return port

    def add_line(self, p1, p2, *,
                 color: str = 'black', dasharray: str = 'SOLID',
                 thickness: str = '02_PT', port: str = '', cond: str = 'true',
                 arrow_head: Optional[Tuple[int, int]] = None):
        """
        Add a line to the component graphics.
        """

        if p1 == p2:
            raise ValueError("End-points must be different")
        if arrow_head is not None:
            if p1[0] != p2[0] and p1[1] != p2[1]:
                raise ValueError("Arrowhead requires horizontal/vertical line")

        line = self.create_component(Gfx.Line)
        line.vertices(p1, p2)
        line.parameters(color=color, dasharray=dasharray, thickness=thickness,
                        port=port, cond=cond)
        if arrow_head:
            length, width = arrow_head
            if p1[1] == p2[1]:
                x = p2[0] + length if p1[0] > p2[0] else p2[0] - length
                p3 = x, p2[1] - width
                p4 = x, p2[1] + width
            else:
                y = p2[1] + length if p1[1] > p2[1] else p2[1] - length
                p3 = p2[0] - width, y
                p4 = p2[0] + width, y

            self.add_line(p2, p3, color=color, dasharray=dasharray,
                          thickness=thickness, port=port, cond=cond)
            self.add_line(p2, p4, color=color, dasharray=dasharray,
                          thickness=thickness, port=port, cond=cond)

        return line

    def add_rectangle(self, p1, p2, *,
                      color: str = 'black', dasharray: str = 'SOLID',
                      thickness: str = '02_PT', port: str = '',
                      fill_style: str = 'HOLLOW', fill_fg: str = 'black',
                      fill_bg: str = 'black', cond: str = 'true'):
        """
        Add a rectangle to the component graphics.
        """

        x, y = min(p1[0], p2[0]), min(p1[1], p2[1])
        w, h = max(p1[0] - x, p2[0] - x, 1), max(p1[1] - y, p2[1] - y, 1)
        rect = self.create_component(Gfx.Rect)
        rect.location = x, y
        rect.size = w, h
        rect.parameters(color=color, dasharray=dasharray, thickness=thickness,
                        fill_style=fill_style, fill_fg=fill_fg, fill_bg=fill_bg,
                        port=port, cond=cond)
        return rect

    def add_text(self, location, text, *, cond: str = 'true',
                 color: str = 'black', anchor: str = 'LEFT',
                 full_font: str = 'Tahoma, 10pt', angle: float = 0.0):

        """
        Add a text label to the component graphics.
        """

        label = self.create_component(Gfx.Text)
        label.location = location
        label.parameters(text=text, cond=cond, color=color, anchor=anchor,
                         full_font=full_font, angle=angle)
        return label


#===============================================================================
# Graphics Component
#===============================================================================

class GfxComponent(ZComponent, MovableMixin):
    """
    A component which can exist on a User Component's Definition's GfxCanvas.

    Includes visible components (lines, text, curves, ...) and invisible
    components (ports).

    .. versionadded:: 2.2
    """

    def __repr__(self):
        return "{}#{}".format(self.__class__.__name__, self.iid)

    location = rmi_property(True, True, name='location')


#===============================================================================
# Graphics Component
#===============================================================================

class Port(GfxComponent):
    """
    An Input, Output or Electrical connection to the component.

    .. versionadded:: 2.2
    """

    def _param_codec(self):
        return FormCodec.gfx_port(self)

#===============================================================================
# Graphical Shapes Component
#===============================================================================

class GfxBase(GfxComponent):
    """
    Superclass for lines, rectangles, ellipses, arcs and other shapes.

    .. versionadded:: 2.2
    """

    @rmi
    def _vertices(self, *args):
        pass

    def vertices(self, *vertices):
        """GfxBase.vertices([vertices])

        Set or get the vertices of the a graphic element

        Parameters:
            vertices (List[x,y]): a list of (x,y) coordinates (optional)

        Returns:
            List[x,y]: A list of (x,y) coordinates.
        """

        if len(vertices) == 0:
            vertices = list(map(Point._make, self._vertices()))
        else:
            # List of vanilla (x, y) tuples
            vertices = [(vtx[0], vtx[1]) for vtx in vertices]
            self._vertices(vertices)
        return vertices

#-------------------------------------------------------------------------------
# Graphical Line Component
#-------------------------------------------------------------------------------

class Line(GfxBase):
    """
    The Graphic Canvas Line Component

    .. versionadded:: 2.2
    """

    def _param_codec(self):
        return FormCodec.gfx_line(self)


#-------------------------------------------------------------------------------
# Graphical Rect Component
#-------------------------------------------------------------------------------

class Rect(GfxBase, SizeableMixin):
    """
    The Graphic Canvas Rectangle Component

    .. versionadded:: 2.2
    """

    def _param_codec(self):
        return FormCodec.gfx_rect(self)


#-------------------------------------------------------------------------------
# Graphical Oval Component
#-------------------------------------------------------------------------------

class Oval(GfxBase):
    """
    The Graphic Canvas Oval Component

    .. versionadded:: 2.2
    """

    def _param_codec(self):
        return FormCodec.gfx_oval(self)


#-------------------------------------------------------------------------------
# Graphical Path Component
#-------------------------------------------------------------------------------

class Arc(GfxBase):
    """
    The Graphic Canvas Arc Component

    .. versionadded:: 2.2
    """

    def _param_codec(self):
        return FormCodec.gfx_arc(self)


#-------------------------------------------------------------------------------
# Graphical "Shape" Component
#-------------------------------------------------------------------------------

class Shape(GfxBase):
    """
    The Graphic Canvas General Shape Component

    May represent a Bezier, RectRound, TriangleRight, TriangleIso, Diamond,
    Parallelogram, Trapezoid, Pentagon, Hexagon, ArrowUp, ArrowRight,
    ArrowDown, ArrowLeft, Star4, Star5, Star6, SpeachRect, SpeachOval,
    Heart, Lightning, or Constant.

    .. versionadded:: 2.2
    """

    def _param_codec(self):
        return FormCodec.gfx_shape(self)


#===============================================================================
# Graphic Text Component
#===============================================================================

class Text(GfxComponent):
    """
    The Graphic Canvas Text Component

    .. versionadded:: 2.2
    """

    def _param_codec(self):
        return FormCodec.gfx_text(self)
