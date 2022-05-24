#===============================================================================
# Component Wizard
#===============================================================================

"""
================
Component Wizard
================

.. versionadded:: 2.2
"""


#===============================================================================
# Imports
#===============================================================================

from enum import IntEnum
from typing import List, Iterable, Tuple, Dict, Union

import xml.etree.ElementTree as ET
import mhi.common.cdata                    # pylint: disable=unused-import

from .types import NodeType, Electrical, Signal
from .types import Align, Side, LineStyle, FillStyle


#===============================================================================
# Data types
#===============================================================================

class _Int18(int):
    def __new__(cls, val):
        val = int(val)
        if val % 18 != 0:
            raise ValueError("Not a multiple of 18")
        return super().__new__(cls, val // 18)
    def __str__(self):
        return str(self * 18)

_COLOUR = {
    Signal.ELECTRICAL: 'Black',
    Signal.LOGICAL: 'Purple',
    Signal.INTEGER: 'Blue',
    Signal.REAL: 'Green',
    Signal.COMPLEX: 'Orange',
    Signal.UNKNOWN: 'Black',
    }


#===============================================================================
# Definition Node
#===============================================================================

class _DefnNode:                        # pylint: disable=too-few-public-methods

    __slots__ = ('_parent', '_node')

    def __init__(self, parent, node):
        self._parent = parent
        self._node = node

    def _find_xpath(self, xpath):
        return self._node.find(xpath) if xpath != '.' else self._node

    def _create_paramlist(self, node=None, **kwargs):
        if node is None:
            node = self._node
        paramlist = ET.SubElement(node, 'paramlist')
        for key, val in kwargs.items():
            ET.SubElement(paramlist, 'param', name=key, value=str(val))
        return paramlist


    #---------------------------------------------------------------------------
    # Paramlist parameters
    #---------------------------------------------------------------------------
    def _set_param(self, name, value, kind):
        paramlist = self._node.find('paramlist')
        if paramlist is None:
            raise ValueError("Node has no parameter list")

        xpath = "param[@name={!r}]".format(name)
        node = paramlist.find(xpath)
        if value is not None:
            if node is None:
                node = ET.SubElement(paramlist, 'param')
                node.set('name', name)

            if issubclass(kind, IntEnum):
                if isinstance(value, str):
                    value = kind[value.upper()].value
                elif isinstance(value, IntEnum):
                    value = value.value
            elif isinstance(value, bool):
                value = "true" if value else "false"
            node.set("value", str(value))
        elif node is not None:
            paramlist.remove(node)

    def _get_param(self, name, kind):
        xpath = "paramlist/param[@name={!r}]".format(name)
        node = self._find_xpath(xpath)
        if node is None:
            return None

        value = node.get("value")
        if issubclass(kind, IntEnum):
            value = int(value)

        return kind(value)


    #---------------------------------------------------------------------------
    # Attributes
    #---------------------------------------------------------------------------
    def _set_attr(self, xpath, attr_name, value, kind):
        node = self._find_xpath(xpath)
        if node is None:
            raise ValueError("Invalid path: " + xpath + "/@" + attr_name)

        if isinstance(value, bool):
            value = "true" if value else "false"
        if value is None:
            del node.attrib[attr_name]
        else:
            if issubclass(kind, IntEnum):
                if isinstance(value, str):
                    value = kind[value.upper()].value
                elif isinstance(value, IntEnum):
                    value = value.value
            node.set(attr_name, str(value))

    def _get_attr(self, xpath, attr_name, kind, default):
        node = self._find_xpath(xpath)
        if node is None:
            raise ValueError("Invalid path: " + xpath + "/@" + attr_name)
        value = node.get(attr_name)
        if value is not None:
            if kind == bool:
                value = value.lower() == "true"
            elif issubclass(kind, IntEnum):
                value = int(value)
        else:
            value = default

        return kind(value) if value is not None else default


    #---------------------------------------------------------------------------
    # CDATA Child
    #---------------------------------------------------------------------------
    def _set_cdata_child(self, tag, value):
        node = self._find_xpath(tag)
        if value is not None:
            if node is None:
                node = ET.SubElement(self._node, tag)
            else:
                for child in list(node):
                    node.remove(child)
            ET.CDATA(node, value)
        elif node is not None:
            self._node.remove(node)

    def _get_cdata_child(self, tag):
        node = self._find_xpath(tag)
        if node is None:
            return None
        return ''.join(node.itertext())


#-------------------------------------------------------------------------------
# Paramlist parameter
#-------------------------------------------------------------------------------

def _param(name, kind=str):

    class Param:
        """
        Parameter

        <param name='name' value='value'/>
        """

        def __init__(self, func):
            self.__doc__ = func.__doc__

        def __set__(self, obj, value):
            obj._set_param(name, value, kind)

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            return obj._get_param(name, kind)

    def wrapper(function):
        return Param(function)

    return wrapper


#-------------------------------------------------------------------------------
# Attribute
#-------------------------------------------------------------------------------

def _attribute(xpath, attr, kind=str, default=None):

    class Attribute:
        """
        Attribute

        <tag attr_name='attr_value' />
        """

        def __init__(self, func, xpath, attr, kind, default):
            self.__doc__ = func.__doc__
            self.xpath = xpath
            self.attr = attr
            self.kind = kind
            self.default = default

        def __set__(self, obj, value):
            obj._set_attr(self.xpath, self.attr, value, kind)

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            return obj._get_attr(self.xpath, self.attr, self.kind, self.default)

    def wrapper(function):
        return Attribute(function, xpath, attr, kind, default)

    return wrapper


#-------------------------------------------------------------------------------
# CData Child
#-------------------------------------------------------------------------------

def _cdata_child(tag):

    class CDataChild:
        """
        CData

        <tag><[CDATA[value]]></tag>
        """
        def __init__(self, func, tag):
            self.__doc__ = func.__doc__
            self.tag = tag

        def __set__(self, obj, value):
            obj._set_cdata_child(self.tag, value)

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self
            return obj._get_cdata_child(self.tag)

    def wrapper(function):
        return CDataChild(function, tag)

    return wrapper


#===============================================================================
# Component Wizard
#===============================================================================

class UserDefnWizard(_DefnNode):

    """
    User Definition construction wizard

    Usage::

        wizard = UserDefnWizard("definition_name")
        wizard.description = "A multiplicative gain factor component"
        wizard.port.input(-2, 0, "In", Signal.REAL)
        wizard.port.output(2, 0, "Out", Signal.REAL)
        config = wizard.category.add("Configuration")
        config.real('Gain', description="Gain factor")
        wizard.graphics.text("Gain", 0, 4)
        wizard.script['Fortran'] = "      $Out = $In * $Gain"

        defn = wizard.create_definition(project)

        canvas.create_component(defn, x, y)

    .. versionadded:: 2.2
    """

    __slots__ = ('_ports', '_graphics',
                 '_categories', '_parameter',
                 '_scripts', '_module')

    def __init__(self, name: str, *, module: bool = False):
        root = ET.Element('Definition', classid='UserCmpDefn',
                          name=name, build='', crc='0', view='false',
                          instances='0', date='0', id='0')
        super().__init__(None, root)

        self._create_paramlist(root, Description='')

        self._graphics = UserDefnWizard.Graphics(self)
        self._ports = UserDefnWizard.Ports(self, self._graphics)
        self._categories = UserDefnWizard.Categories(self)
        self._parameter = UserDefnWizard.Parameters(self._categories)
        self._scripts = UserDefnWizard.Scripts(self)
        self._module = module

        self.form_category_width = 180      # pylint: disable=assigning-non-slot
        self.form_help_width = 490          # pylint: disable=assigning-non-slot

        configuration = self.category.add('Configuration', enable="true")
        configuration.text('Name', description="Name of the component")


    @staticmethod
    def _paramlist(node, **kwargs):
        paramlist = ET.SubElement(node, 'paramlist')
        for key, val in kwargs.items():
            ET.SubElement(paramlist, 'param', name=key, value=str(val))
        return paramlist


    #--------------------------------------------------------------------------
    # Definition Attributes
    #--------------------------------------------------------------------------

    @_attribute('.', 'name')
    def name(self):
        """
        Definition name (hint)

        When the definition is created, PSCAD may change the definition
        name to ensure it is unique.
        """


    #--------------------------------------------------------------------------
    # Module
    #--------------------------------------------------------------------------

    @property
    def module(self) -> bool:
        """
        Flag indicating this definition will be a module with a user canvas.

        .. versionadded:: 2.5
        """
        return self._module

    @module.setter
    def module(self, value):
        if not isinstance(value, bool):
            raise ValueError("module must be True or False")

        if value and self._scripts:
            raise ValueError("Scripts exist; cannot be a module")

        self._module = value

    #--------------------------------------------------------------------------
    # Param List
    #--------------------------------------------------------------------------

    @_param('Description')
    def description(self):
        """Component definition description"""


    #--------------------------------------------------------------------------
    # Port
    #--------------------------------------------------------------------------

    class Port(_DefnNode):
        """Port()

        Component Input/Output/Electrical connections
        """

        __slots__ = ('arrow', '_side')  # Prevent assigning to wrong field-names

        @classmethod
        def _create(cls, parent, x, y):
            node = ET.SubElement(parent._node, 'Port') # pylint: disable=protected-access
            port = cls(parent, node)
            port._create_paramlist()          # pylint: disable=protected-access

            port.x = x * 18                 # pylint: disable=assigning-non-slot
            port.y = y * 18                 # pylint: disable=assigning-non-slot

            port.arrow = None   # pylint: disable=attribute-defined-outside-init
            port.side = Side.AUTO

            return port

        @_attribute('.', 'x', _Int18)
        def x(self):                              # pylint: disable=invalid-name
            """Port X coordinate"""

        @_attribute('.', 'y', _Int18)
        def y(self):                              # pylint: disable=invalid-name
            """Port Y coordinate"""

        @_param('Name')
        def name(self):
            """Port name"""

        @_param('dim', int)
        def dim(self):
            """
            Port dimension.

            A dimension of 1 indicates a scalar wire connection.
            A dimension greater than 1 indicates an array wire connection.
            A dimension of 0 inherits the dimesion of the connected wire.
            """

        @_param('internal', bool)
        def internal(self):
            """Used to create electrical nodes with no outside connection"""

        @_param('cond')
        def enable(self):
            """Port enable condition"""

        @_param('mode', NodeType)
        def mode(self):
            """Port node type (ELECTRICAL, INPUT, OUTPUT)"""

        @_param('datatype', Signal)
        def data_type(self):
            """I/O port data type (BOOLEAN, INTEGER, REAL, COMPLEX)"""

        @_param('electype', Electrical)
        def electrical_type(self):
            """Electrical port type (FIXED, SWITCHED, REMOVABLE)"""

        @property
        def side(self):
            """Port label location (NONE, LEFT, ABOVE, BELOW, RIGHT, AUTO)"""
            return self._side

        @side.setter
        def side(self, value):
            if not isinstance(value, Side):
                value = Side[value.upper()]
            self._side = value


    #--------------------------------------------------------------------------
    # Ports
    #--------------------------------------------------------------------------

    class Ports(_DefnNode):
        """Ports()

        Port Container, accessed using the
        :meth:`wizard.port <.UserDefnWizard.port>` property.

        Use ``wizard.port["name"]`` to access a :class:`.Port` by name.

        Since the same port name may exist multiple times with different
        ``enable`` condtions, use ``for port in wizard.port:`` to iterate over
        all defined ports.
        """

        __slots__ = ('_ports', )        # Prevent assigning to wrong field-names

        def __init__(self, parent, graphics):
            super().__init__(self, graphics._node)
            self._ports = []

        def _add(self, x, y, **kwargs):
            if 'arrow' in kwargs:

                if kwargs['arrow'] is True:
                    kwargs['arrow'] = (5, 5)
                elif not kwargs['arrow']:
                    kwargs['arrow'] = None

            port = UserDefnWizard.Port._create(self, x, y) # pylint: disable=protected-access
            for key, value in kwargs.items():
                setattr(port, key, value)
            self._ports.append(port)

        def input(self, x: int, y: int, name: str,
                  data_type: Union[str, Signal],
                  dim: int = 1, enable: str = "true",
                  arrow: Union[bool, Tuple[int, int]] = True):
            """
            Create a new control signal input port
            """

            return self._add(x, y, mode="INPUT", name=name,
                             data_type=data_type, dim=dim, enable=enable,
                             arrow=arrow)

        def output(self, x: int, y: int, name: str,
                   data_type: Union[str, Signal],
                   dim: int = 1, enable: str = "true",
                   arrow: Union[bool, Tuple[int, int]] = False):
            """
            Create a new control signal output port
            """

            return self._add(x, y, mode="OUTPUT", name=name,
                             data_type=data_type, dim=dim, enable=enable,
                             arrow=arrow)

        def electrical(self, x: int, y: int, name: str,
                       electrical_type: Union[str, Electrical] = "FIXED",
                       dim: int = 1, enable: str = "true",
                       internal: bool = False):
            """
            Create a new electrical connection port
            """

            return self._add(x, y, mode="ELECTRICAL", name=name,
                             electrical_type=electrical_type, dim=dim,
                             enable=enable, internal=internal,
                             data_type=Signal.ELECTRICAL)

        def __len__(self):
            return len(self._ports)

        def __iter__(self):
            return iter(self._ports)

        def __getitem__(self, key):
            for port in self._ports:
                if port.name == key:
                    return port
            raise KeyError("No such port")


    #--------------------------------------------------------------------------

    @property
    def port(self):
        """
        Port container.

        Use

        - :meth:`wizard.port.input(X, Y, "port_name", ...) <.Ports.input>`,
        - :meth:`wizard.port.output(X, Y, "port_name", ...) <.Ports.output>`,
        - :meth:`wizard.port.electrical(X, Y, "port_name", ...) <.Ports.electrical>`,

        to add new inputs, outputs, and electrical connection ports.

        Use ``wizard.port["name"]`` to access a :class:`.Port` by name.

        Since the same port name may exist multiple times with different
        ``enable`` condtions, use ``for port in wizard.port:`` to iterate over
        all defined ports.
        """

        return self._ports


    #--------------------------------------------------------------------------
    # Graphics
    #--------------------------------------------------------------------------

    class _GfxNode(_DefnNode):

        __slots__ = ()                  # Prevent assigning to wrong field-names

        @classmethod
        def _create(cls, parent, x, y, class_id, **paramlist):
            node = ET.SubElement(parent._node, 'Gfx', # pylint: disable=protected-access
                                 classid=class_id, x=str(x), y=str(y))
            gfx = cls(parent, node)
            gfx._create_paramlist()           # pylint: disable=protected-access

            for key, value in paramlist.items():
                setattr(gfx, key, value)

            return gfx

        @_attribute('.', 'x', int)
        def x(self):                              # pylint: disable=invalid-name
            """X coordinate"""

        @_attribute('.', 'y', int)
        def y(self):                              # pylint: disable=invalid-name
            """Y coordinate"""

        @_param('cond')
        def enable(self):
            """Visibility condition"""

        @_param('color')
        def color(self):
            """Color"""

    #--------------------------------------------------------------------------
    # Text
    #--------------------------------------------------------------------------

    class Text(_GfxNode):

        """Text()

        A text label
        """

        __slots__ = ()                  # Prevent assigning to wrong field-names

        @classmethod
        def _create(cls, parent, x, y, **paramlist): # pylint: disable=arguments-differ
            text = super()._create(parent, x, y, 'Graphics.Text',
                                   **paramlist)
            return text

        @_param('text')
        def text(self):
            """Text label"""

        @_param('cond')
        def enable(self):
            """Text visibility condition"""

        @_param('anchor', Align)
        def anchor(self):
            """Text anchor (LEFT, CENTER, RIGHT)"""

        @_param('angle', int)
        def angle(self):
            """Text angle (degrees)"""

        @_param('full_font')
        def full_font(self):
            """Text Font"""


    #--------------------------------------------------------------------------
    # _StrokedNode
    #--------------------------------------------------------------------------

    class _StrokedNode(_GfxNode):

        __slots__ = ()                  # Prevent assigning to wrong field-names

        @_param('thickness', int)
        def thickness(self):
            """
            Line thickness

            === ===============
             0  0.2pt
             1  0.4pt
             2  0.6pt
             3  0.8pt
             4  1.0pt
             5  1.2pt
             6  1.4pt
             7  Associated Port
            === ===============
            """

        @_param('dasharray', LineStyle)
        def line_style(self):
            """Line style (SOLID, DOT, DASH, DOTDASH)"""

        @_param('port', str)
        def port(self):
            """Associated port name (for line thickness)"""


    #--------------------------------------------------------------------------
    # _FilledNode
    #--------------------------------------------------------------------------

    class _FilledNode(_GfxNode):

        __slots__ = ()                  # Prevent assigning to wrong field-names

        @_param('fill_fg')
        def foreground(self):
            """Foreground fill color"""

        @_param('fill_bg')
        def background(self):
            """Background fill color"""

        @_param('fill_style', FillStyle)
        def fill_style(self):
            """Fill style (SOLID, HOLLOW, CROSS, HORIZONTAL, VERTICAL, ...)"""


    #--------------------------------------------------------------------------
    # Line
    #--------------------------------------------------------------------------

    class Line(_StrokedNode):

        """Line()

        A straight line
        """

        __slots__ = ()  # Prevent assigning to wrong field-names


        @classmethod
        def _create(cls, parent, *vertices, **paramlist):
            if len(vertices) < 2:
                raise TypeError("At least 2 vertices required")

            x, y = vertices[0]
            line = super()._create(parent, x, y, 'Graphics.Line',
                                   **paramlist)
            for vertex in vertices:
                ET.SubElement(line._node, 'vertex', # pylint: disable=protected-access
                              x=str(vertex[0] - x), y=str(vertex[1] - y))

            return line


    #--------------------------------------------------------------------------
    # Rectangle
    #--------------------------------------------------------------------------

    class Rectangle(_StrokedNode, _FilledNode):

        """Rectangle()

        An axis-aligned rectangle.
        """

        __slots__ = ()  # Prevent assigning to wrong field-names

        @_attribute('.', 'w', int)
        def width(self):
            """Width"""

        @_attribute('.', 'h', int)
        def height(self):
            """Height"""

        @classmethod
        def _create(cls, parent, x1, y1, x2, y2, **paramlist): # pylint: disable=arguments-differ
            x, y = min(x1, x2), min(y1, y2)
            w, h = max(x1, x2) - x, max(y1, y2) - y

            rect = super()._create(parent, x, y, 'Graphics.Rectangle',
                                   width=w, height=h, **paramlist)
            return rect


    #--------------------------------------------------------------------------
    # Graphics
    #--------------------------------------------------------------------------

    _GFX = {
        'Graphics.Text': Text,
        'Graphics.Line': Line,
        'Graphics.Rectangle': Rectangle,
        }

    class Graphics(_DefnNode):
        """Graphics()

        Container for graphical elements, accessed using the
        :meth:`wizard.graphics <.UserDefnWizard.graphics>` property.

        The current defined graphic shapes (excluding port lines & arrows)
        may be iterated over using ``for shape in wizard.graphics:``
        """

        __slots__ = ('_tmp_gfx',)       # Prevent assigning to wrong field-names

        def __init__(self, parent):
            node = ET.SubElement(parent._node, 'graphics')
            super().__init__(parent, node)
            self._tmp_gfx = []

        def __len__(self):
            return len(self._node.iterfind('Gfx'))

        def _find_all(self, class_id):
            cls = UserDefnWizard._GFX[class_id] # pylint: disable=protected-access
            xpath = "Gfx[@classid={!r}]".format(class_id)
            for gfx in self._node.iterfind(xpath):
                yield cls(self, gfx)

        def __iter__(self):
            for gfx in self._node.find('Gfx'):
                class_id = gfx.get('classid')
                yield UserDefnWizard._GFX[class_id](self, gfx)

        def text(self, text: str, x: int = 0, y: int = 5, *,
                 color: str = 'Black', enable: str = 'true', angle: int = 0,
                 anchor: Union[str, Align] = Align.CENTER,
                 full_font: str = "Tahoma, 12world"):
            """
            Create a text label.
            """

            return UserDefnWizard.Text._create(self, x, y, text=text, # pylint: disable=protected-access
                                               enable=enable, color=color,
                                               angle=angle, anchor=anchor,
                                               full_font=full_font)

        def line(self, x1: int, y1: int, x2: int, y2: int, *,
                 enable: str = "true", color: str = "black",
                 line_style: Union[str, LineStyle] = LineStyle.SOLID,
                 thickness: int = 0, port: str = ""):
            """
            Create a line between [x1,y1] and [x2,y2].
            """

            return UserDefnWizard.Line._create(self, (x1, y1), (x2, y2), # pylint: disable=protected-access
                                               enable=enable, color=color,
                                               line_style=line_style,
                                               thickness=thickness,
                                               port=port)


        def arrow(self, x1: int, y1: int, x2: int, y2: int,
                  length: int = 5, width: int = 5, *,
                  enable: str = "true", color: str = "black",
                  line_style: Union[str, LineStyle] = LineStyle.SOLID,
                  thickness: int = 0, port: str = ""):
            """
            Create an arrow from [x1,y1] to [x2,y2].
            """

            if y1 == y2:
                x3 = x4 = x2 - length if x1 < x2 else x2 + length
                y3, y4 = y2 + width, y2 - width
            else:
                y3 = y4 = y2 - length if y1 < y2 else y2 + length
                x3, x4 = x2 + width, x2 - width

            line_1 = self.line(x1, y1, x2, y2, enable=enable, color=color,
                               line_style=line_style, thickness=thickness,
                               port=port)
            line_2 = self.line(x2, y2, x3, y3, enable=enable, color=color,
                               line_style=line_style, thickness=thickness,
                               port=port)
            line_3 = self.line(x2, y2, x4, y4, enable=enable, color=color,
                               line_style=line_style, thickness=thickness,
                               port=port)
            return line_1, line_2, line_3


        def rectangle(self, x1: int, y1: int, x2: int, y2: int,
                      enable: str = "true", color: str = "black",
                      line_style: Union[str, LineStyle] = LineStyle.SOLID,
                      thickness: int = 0, port: str = '',
                      foreground: str = "Black",
                      background: str = "White",
                      fill_style: int = 0):
            """
            Create a rectangle between corners [x1,y1] and [x2,y2].
            """

            return UserDefnWizard.Rectangle._create(self, x1, y1, x2, y2, # pylint: disable=protected-access
                                                    enable=enable, color=color,
                                                    line_style=line_style,
                                                    thickness=thickness,
                                                    port=port,
                                                    foreground=foreground,
                                                    background=background,
                                                    fill_style=fill_style)


        def _create_lead(self, port, x1, y1, x2, y2): # pylint: disable=too-many-branches, too-many-statements
            colour = _COLOUR[port.data_type]
            attrs = dict(color=colour, port=port.name, enable=port.enable)
            if x1 != x2 or y1 != y2:
                if port.mode == NodeType.ELECTRICAL or not port.arrow:
                    gfx = self.line(x1, y1, x2, y2, **attrs)
                    self._tmp_gfx.append(gfx)
                elif port.mode == NodeType.INPUT:
                    gfx = self.arrow(x1, y1, x2, y2, *port.arrow, **attrs)
                    self._tmp_gfx.extend(gfx)
                else:
                    gfx = self.arrow(x2, y2, x1, y1, *port.arrow, **attrs)
                    self._tmp_gfx.extend(gfx)

            if port._side != Side.NONE:       # pylint: disable=protected-access
                attrs = dict(color=colour, enable=port.enable)
                anchor = Align.CENTER
                x, y = x1, y1 - 3
                auto = port._side == Side.AUTO # pylint: disable=protected-access
                if port._side == Side.LEFT or auto and y1 < y2: # pylint: disable=protected-access
                    x = min(x1, x2) - 3
                    if y1 == y2 and x1 > x2:
                        y = y1 + 5
                    else:
                        y = y2 - 3 if y1 < y2 else y2 + 12
                    anchor = Align.RIGHT
                elif port._side == Side.RIGHT or auto and y1 > y2: # pylint: disable=protected-access
                    x = max(x1, x2) + 3
                    if y1 == y2 and x1 < x2:
                        y = y1 + 5
                    else:
                        y = y2 - 3 if y1 < y2 else y2 + 12
                    anchor = Align.LEFT
                elif port._side == Side.TOP or auto and x1 > x2: # pylint: disable=protected-access
                    y = min(y1, y2) - 3
                    if x1 == x2:
                        x = x1
                    elif x1 < x2:
                        x = x2 - 3
                        anchor = Align.RIGHT
                    else:
                        x = x2 + 3
                        anchor = Align.LEFT
                elif port._side == Side.BOTTOM or auto and x1 < x2: # pylint: disable=protected-access
                    y = max(y1, y2) + 12
                    if x1 == x2:
                        x = x1
                    elif x1 < x2:
                        x = x2 - 3
                        anchor = Align.RIGHT
                    else:
                        x = x2 + 3
                        anchor = Align.LEFT

                gfx = self.text(port.name, x, y, anchor=anchor, **attrs)
                self._tmp_gfx.append(gfx)


        def _create_leads(self):

            grid = 18

            points = [(port.x * grid, port.y * grid)
                      for port in self._parent.port]

            points.extend((text.x, text.y)
                          for text in self._find_all('Graphics.Text'))

            points.extend(((-18, -18), (+18, +18), (-5, -5), (5, 5)))
            left = min(pnt[0] for pnt in points)
            right = max(pnt[0] for pnt in points)
            top = min(pnt[1] for pnt in points)
            btm = max(pnt[1] for pnt in points)
            x_edge = {left, right}

            x1 = min(pnt[0] for pnt in points if pnt[0] > left) - 4
            x2 = max(pnt[0] for pnt in points if pnt[0] < right) + 4
            y1 = min(pnt[1] for pnt in points if pnt[1] > top or pnt[0] in x_edge) - 4
            y2 = max(pnt[1] for pnt in points if pnt[1] < btm or pnt[0] in x_edge) + 4

            rect = self.rectangle(x1, y1, x2, y2)
            self._tmp_gfx.append(rect)

            for port in self._parent.port:
                x, y = port.x * grid, port.y * grid
                if x == left:
                    self._create_lead(port, x, y, x1, y)
                elif y == top:
                    self._create_lead(port, x, y, x, y1)
                elif x == right:
                    self._create_lead(port, x, y, x2, y)
                elif y == btm:
                    self._create_lead(port, x, y, x, y2)
                else:
                    self._create_lead(port, x, y, x, y)

        def _remove_tmp_gfx(self):
            root = self._node
            for gfx in self._tmp_gfx:
                root.remove(gfx._node)        # pylint: disable=protected-access
            self._tmp_gfx.clear()


    #---------------------------------------------------------------------------

    @property
    def graphics(self):
        """
        Graphics container.

        The current defined graphic shapes (excluding port lines & arrows)
        may be iterated over using ``for shape in wizard.graphics:``

        Use

        - :meth:`wizard.graphics.text(...) <.Graphics.text>`,
        - :meth:`wizard.graphics.line(...) <.Graphics.line>`,
        - :meth:`wizard.graphics.arrow(...) <.Graphics.arrow>`,
        - :meth:`wizard.graphics.rectangle(...) <.Graphics.rectangle>`,

        to add new text, lines, arrows, and rectangles.

        .. note::

            Lines & arrows will be created for ports automatically.
        """

        return self._graphics


    #--------------------------------------------------------------------------
    # Parameter Form
    #--------------------------------------------------------------------------

    @_attribute('form', 'name')
    def form_caption(self):
        """Parameter Form's Caption"""

    @_attribute('form', 'w', int)
    def form_width(self):
        """Parameter Form's width"""

    @_attribute('form', 'h', int)
    def form_height(self):
        """Parameter Form height"""

    @_attribute('form', 'splitter', int)
    def form_splitter(self):
        """Parameter Form default splitter position"""

    @_attribute('form', 'category-width', int)
    def form_category_width(self):
        """Parameter Form's category tree width"""

    @_attribute('form', 'help-width', int)
    def form_help_width(self):
        """Parameter Form's dynamic help panel width"""


    #--------------------------------------------------------------------------
    # Parameter
    #--------------------------------------------------------------------------

    class Parameter(_DefnNode):
        """Parameter()

        Component parameter
        """

        __slots__ = ()  # Prevent assigning to wrong field-names

        @classmethod
        def _create(cls, parent, type_, name):
            node = ET.SubElement(parent._node, 'parameter', # pylint: disable=protected-access
                                 type=type_, name=name, desc=name)
            return cls(parent, node)

        @_attribute('.', 'type')
        def type(self):
            """Type of the Parameter"""

        @_attribute('.', 'name')
        def name(self):
            """Parameter name"""

        @_attribute('.', 'desc')
        def description(self):
            """Parameter description"""

        @_attribute('.', 'group')
        def group(self):
            """Parameter group"""

        @_attribute('.', 'min', float)
        def minimum(self):
            """Parameter minimum limit"""

        @_attribute('.', 'max', float)
        def maximum(self):
            """Parameter maximum limit"""

        @_attribute('.', 'unit')
        def units(self):
            """Parameter units"""

        @_attribute('.', 'helpmode')
        def help_mode(self):
            """Parameter help mode (``Overwrite`` or ``Append``)"""

        @_cdata_child('value')
        def value(self):
            """Parameter description"""

        @_cdata_child('cond')
        def enable(self):
            """Parameter enable condition"""

        @_cdata_child('vis')
        def visible(self):
            """Parameter visibility condition"""

        @_cdata_child('help')
        def help_text(self):
            """Parameter Help text"""

        @_attribute('.', 'allowemptystr', bool)
        def allow_empty_strings(self):
            """Is Text Parameter allowed to be empty?"""

        @_cdata_child('regex')
        def regex(self):
            """Text Parameter regular-expression filter"""

        @_cdata_child('error_msg')
        def error_message(self):
            """Text Parameter invalid input error message"""

        @property
        def choices(self):
            """Choice parameter choices"""
            return {key: val
                    for node in self._node.iterfind('choice')
                    for key, val in "".join(node.itertext()).split(" = ", 1)
                    }

        @choices.setter
        def choices(self, choices):
            for node in list(self._node.iterfind('choice')):
                self._node.remove(node)

            if choices:
                for key, val in choices.items():
                    node = ET.SubElement(self._node, 'choice')
                    ET.CDATA(node, "{} = {}".format(key, val))

        def __str__(self):
            return "{}: {} ({})".format(self.name, self.description, self.type)

        def __repr__(self):
            return "Parameter<{}>".format(self)


    #--------------------------------------------------------------------------
    # Category
    #--------------------------------------------------------------------------

    class Category(_DefnNode):
        """Category()

        Component parameter form category, accessed using the
        :meth:`wizard.category <.UserDefnWizard.category>` property.

        After creating a category using
        :meth:`category = wizard.category.add("category_name", ...) <.Categories.add>`,
        use

        - :meth:`category.text("param_name", ...) <.Category.text>`,
        - :meth:`category.logical("param_name", ...) <.Category.logical>`,
        - :meth:`category.boolean("param_name", ...) <.Category.boolean>`,
        - :meth:`category.choice("param_name", ...) <.Category.choice>`,
        - :meth:`category.integer("param_name", ...) <.Category.integer>`,
        - :meth:`category.real("param_name", ...) <.Category.real>`,

        to add parameters to that category.

        """

        __slots__ = ()  # Prevent assigning to wrong field-names

        @classmethod
        def _create(cls, parent, name):
            node = ET.SubElement(parent._node, 'category', name=name) # pylint: disable=protected-access
            return cls(parent, node)

        @_attribute('.', 'name')
        def name(self):
            """Category Name"""

        @_attribute('.', 'level', int, 0)
        def level(self):
            """Category Level, for indenting category tree nodes"""

        @_cdata_child('cond')
        def enable(self):
            """Category enable condition"""

        def __len__(self):
            return len(self._node.findall('parameter'))

        def keys(self) -> List[str]:
            """
            Parameter names
            """
            return [node.get('name')
                    for node in self._node.iterfind('parameter')]

        def _find(self, key):
            return self._node.find('parameter[@name={!r}]'.format(key))

        def __contains__(self, key):
            return self._find(key) is not None

        def __getitem__(self, key):
            node = self._find(key)
            if node is None:
                raise KeyError("Parameter not found")
            return UserDefnWizard.Parameter(self, node)

        def __delitem__(self, key):
            node = self._find(key)
            if node is None:
                raise KeyError("Parameter not found")
            self._node.remove(node)

        def _add(self, type_, name, **kwargs):
            param = None
            if name.lower() == "name" and type_ == 'Text':
                categories = self._parent
                first_category = next(iter(categories._node), None) # pylint: disable=protected-access
                if first_category == self._node and len(self) == 1:
                    if 'Name' in self:
                        param = self['Name']

            if param is None:
                param = UserDefnWizard.Parameter._create(self, type_, name) # pylint: disable=protected-access

            for key, value in kwargs.items():
                if value is not None:
                    setattr(param, key, value)

            return param

        # pylint: disable=redefined-builtin

        def text(self, name: str, *,
                 description: str = None, group: str = '',
                 enable: str = None, visible: str = None,
                 value: str = '',
                 help: str = None, help_mode: str = None,
                 regex: str = None, allow_empty_strings: bool = True,
                 minimum_length: int = None, maximum_length: int = None,
                 error_msg: str = None):
            """
            Add a text parameter to the category
            """

            return self._add('Text', name,
                             description=description, group=group,
                             enable=enable, visible=visible,
                             value=value, help=help, help_mode=help_mode,
                             regex=regex, error_msg=error_msg,
                             minimum=minimum_length, maximum=maximum_length,
                             allow_empty_strings=allow_empty_strings)

        def logical(self, name: str, *,
                    description: str = None, group: str = '',
                    enable: str = None, visible: str = None,
                    value: str = '.TRUE.',
                    help: str = None, help_mode: str = None):
            """
            Add a logical parameter to the category
            """

            return self._add('Logical', name,
                             description=description, group=group,
                             enable=enable, visible=visible,
                             value=value, help=help, help_mode=help_mode)

        def boolean(self, name: str, *,
                    description: str = None, group: str = '',
                    enable: str = None, visible: str = None,
                    true_text: str = "Show", false_text: str = "Hide",
                    value: str = '.TRUE.',
                    help: str = None, help_mode: str = None):
            """
            Add a boolean parameter to the category.

            By default, boolean parameters display ``Show`` or ``Hide`` when
            true or false, but these may be changed using the
            ``true_text="...", false_text="..."`` parameters.
            """

            return self._add('Boolean', name,
                             description=description, group=group,
                             enable=enable, visible=visible,
                             value=value, help=help, help_mode=help_mode,
                             choices=dict(true=true_text, false=false_text))

        def choice(self, name: str, *,
                   choices: Dict[int, str],
                   description: str = None, group: str = '',
                   enable: str = None, visible: str = None,
                   value: str = '',
                   help: str = None, help_mode: str = None):
            """
            Add a choice parameter to the category.

            The choices must be specified by passing a dictionary to the
            ``choices={...}`` parameter.  Dictionary keys should be integers,
            and the values the text to display for each key.
            """

            return self._add('Choice', name,
                             description=description, group=group,
                             enable=enable, visible=visible,
                             value=value, help=help, help_mode=help_mode,
                             choices=choices)

        def integer(self, name: str, *,
                    description: str = None, group: str = '',
                    enable: str = None, visible: str = None,
                    value: int = 0,
                    help: str = None, help_mode: str = None,
                    minimum: int = -2147483647, maximum: int = 2147483647):
            """
            Add an integer parameter to the category.
            """

            return self._add('Integer', name,
                             description=description, group=group,
                             enable=enable, visible=visible,
                             value=value, help=help, help_mode=help_mode,
                             minimum=minimum, maximum=maximum)

        def real(self, name: str, *,
                 description: str = None, group: str = '',
                 enable: str = None, visible: str = None,
                 value: float = 0.0,
                 help: str = None, help_mode: str = None,
                 minimum: float = -1.0e308, maximum: float = 1.0e308,
                 units: str = None):
            """
            Add an real parameter to the category.
            """

            return self._add('Real', name,
                             description=description, group=group,
                             enable=enable, visible=visible,
                             value=value, help=help, help_mode=help_mode,
                             minimum=minimum, maximum=maximum, units=units)

        # pylint: enable=redefined-builtin

        def __str__(self):
            return "Category[{!r}]".format(self.name)

        def __repr__(self):
            return "Category[{!r}]".format(self.name)


    #--------------------------------------------------------------------------
    # Categories
    #--------------------------------------------------------------------------

    class Categories(_DefnNode):
        """Categories()

        Component parameter form category container, accessed using the
        :meth:`wizard.category <.UserDefnWizard.category>` property.
        """

        __slots__ = ()  # Prevent assigning to wrong field-names

        def __init__(self, parent):
            node = ET.SubElement(parent._node, 'form',
                                 w='320', h='400', splitter='60')
            super().__init__(parent, node)

        def __len__(self):
            return len(self._node)

        def _find(self, key):
            return self._node.find("category[@name={!r}]".format(key))

        def __contains__(self, key):
            return self._find(key) is not None

        def __getitem__(self, key):
            node = self._find(key)
            if node is None:
                raise KeyError("No such category")
            return UserDefnWizard.Category(self, node)

        def __delitem__(self, key):
            node = self._find(key)
            if node is None:
                raise KeyError("No such category")
            self._node.remove(node)

        def __iter__(self):
            for node in self._node.iterfind("category"):
                yield UserDefnWizard.Category(self, node)

        def keys(self) -> List[str]:
            """
            List of Form Category names
            """

            return [node.get('name')
                    for node in self._node.iterfind("category")]

        def add(self, name, *, enable: str = "true", level: int = None):
            """
            Add a new category
            """

            if len(self) == 1 and name in self:
                category = self[name]
            else:
                category = UserDefnWizard.Category._create(self, name) # pylint: disable=protected-access

            category.enable = enable
            if level is not None:
                category.level = level
            return category

        def __repr__(self):
            return "{" + ", ".join("{!r}: Category[...]".format(name)
                                   for name in self.keys()) + "}"


    #---------------------------------------------------------------------------

    @property
    def category(self):
        """
        Component parameter form category container

        Use :meth:`wizard.category.add("category_name", ...) <.Categories.add>`,
        to add categories to the form.
        Parameters may then be added to that category object.

        Use ``wizard.category["name"]`` to access a :class:`category <.Category>`
        by name.
        """

        return self._categories


    #--------------------------------------------------------------------------
    # Parameters
    #--------------------------------------------------------------------------

    class Parameters:
        """Parameters()

        Parameters container, accessed using the
        :meth:`wizard.parameter <.UserDefnWizard.parameter>` property.

        .. note::

            Parameters can only be added to a category object.
            Use :meth:`wizard.category.add(...) <.Categories.add>` to create the
            category, then add parameters to that category object.
        """

        __slots__ = ('_categories', )  # Prevent assigning to wrong field-names

        def __init__(self, categories):
            self._categories = categories

        def keys(self) -> List[str]:
            """
            List of parameter names
            """

            keys = []
            for category in self._categories:
                keys.extend(category.keys())
            return keys

        def __len__(self):
            return len(self.keys())

        def _find(self, key):
            for category in self._categories:
                node = category._find(key)    # pylint: disable=protected-access
                if node is not None:
                    return category, node
            return None, None

        def __contains__(self, key):
            xpath = 'category/parameter[@name={!r}]'.format(key)
            return self._categories.find(xpath) is not None

        def __getitem__(self, key):
            category, node = self._find(key)
            if node is None:
                raise KeyError("No such parameter")
            return UserDefnWizard.Parameter(category, node)

        def __delitem__(self, key):
            category, node = self._find(key)
            if node is None:
                raise KeyError("No such parameter")
            category._node.remove(node)

        def __repr__(self):
            return "{" + ", ".join("{!r}: Parameter[...]".format(name)
                                   for name in self.keys()) + "}"


    #---------------------------------------------------------------------------

    @property
    def parameter(self):
        """
        Component parameter container

        Using ``wizard.parameter["name"]`` to access an existing parameter.

        .. note::

            Parameters can only be added to a category object.
            Use :meth:`wizard.category.add(...) <.Categories.add>` to create the
            category, then add parameters to that category object.
        """

        return self._parameter


    #---------------------------------------------------------------------------
    # Scripts
    #---------------------------------------------------------------------------

    class Scripts(_DefnNode):
        """Scripts()

        Script Section container
        """

        __slots__ = ()  # Prevent assigning to wrong field-names

        SEGMENTS = {'Branch', 'Checks', 'Computations',
                    'Dsdyn', 'Dsout', 'Fortran',
                    'MANA', 'Matrix-Fill', 'Model-Data', 'T-Lines',
                    'Transformers', 'Help', 'FlyBy', 'Comments'}

        def __init__(self, parent):
            node = ET.SubElement(parent._node, 'script')
            super().__init__(parent, node)

        def __len__(self):
            return len(self._node)

        @classmethod
        def _validate_key(cls, key):
            if key not in cls.SEGMENTS:
                raise KeyError("Invalid segment name")

        def _find(self, key):
            self._validate_key(key)
            return self._node.find('segment[@name={!r}]'.format(key))

        def __contains__(self, key):
            return self._find(key) is not None

        def __getitem__(self, key):
            node = self._find(key)
            if node is None:
                raise KeyError("No such script segment")
            return ''.join(node.itertext())

        def __delitem__(self, key):
            node = self._find(key)
            if node is None:
                raise KeyError("No such script segment")
            self._node.remove(node)

        def __setitem__(self, key, value):
            node = self._find(key)
            if node is None:
                node = ET.SubElement(self._node, 'segment',
                                     name=key, classid='CoreSegment')
            for child in list(node):
                node.remove(child)
            ET.CDATA(node, value)

        def keys(self) -> List[str]:
            """
            Currently defined script section names
            """

            return [node.get('name') for node in self._node]

        def __iter__(self):
            for node in self._node:
                yield node.get('name')

        def items(self) -> Iterable[Tuple[str, str]]:
            """
            Generator of script name/value pairs
            """

            for node in self._node:
                yield node.get('name'), ''.join(node.itertext())

        def __repr__(self):
            return "{" + ", ".join("{!r}: Script[...]".format(name)
                                   for name in self.keys()) + "}"


    #---------------------------------------------------------------------------

    @property
    def script(self):
        """
        Component scripts container

        Use ``wizard.script['Fortran'] = '''...'''`` to set a script section.

        Valid sections are: Branch, Checks, Computations, Dsdyn, Dsout,
        Fortran, MANA, Matrix-Fill, Model-Data, T-Lines, Transformers
        Help, FlyBy, and Comments.
        """

        if self._module:
            raise AttributeError("A module do not support scripts")

        return self._scripts


    #--------------------------------------------------------------------------
    # Module
    #--------------------------------------------------------------------------

    def _create_schematic(self):
        schematic_xml = """\
<schematic classid="UserCanvas"><paramlist><param name="show_grid" value="1" />\
<param name="size" value="0" /><param name="orient" value="1" />\
<param name="show_border" value="0" /><param name="show_signal" value="0" />\
<param name="monitor_bus_voltage" value="0" />\
<param name="show_virtual" value="0" /><param name="show_sequence" value="0" />\
<param name="auto_sequence" value="1" /></paramlist><grouping /></schematic>"""
        schematic = ET.fromstring(schematic_xml)

        min_x = min(port.x for port in self.port)
        min_y = min(port.y for port in self.port)

        for port in self.port:
            self._create_port(schematic, port, port.x - min_x, port.y - min_y)

        return schematic

    def _create_port(self, schematic, port, x, y):
        orient = "0"
        x = (x*4 + 5) * 18
        y = (y*4 + 2) * 18

        if port.mode == NodeType.ELECTRICAL:
            defn = "master:xnode"
        elif port.mode == NodeType.INPUT:
            x -= 36
            defn = "master:import"
        else:
            defn = "master:export"
            x += 36
            orient = "2"

        user = ET.SubElement(schematic, "User", classid="UserCmp", id="0",
                             name=defn, x=str(x), y=str(y),
                             w="28", h="33", z="-1", orient=orient,
                             defn=defn, link="-1", q="4", disable="false")
        paramlist = ET.SubElement(user, "paramlist", name="", link="-1",
                                  crc="0")
        ET.SubElement(paramlist, "param", name="Name", value=port.name)


    #--------------------------------------------------------------------------
    # Stringify
    #--------------------------------------------------------------------------
    def _xml(self):
        schematic = None
        if self._module:
            schematic = self._create_schematic()
            self._node.append(schematic)

        self.graphics._create_leads()         # pylint: disable=protected-access
        xml = ET.tostring(self._node, encoding='unicode')
        self.graphics._remove_tmp_gfx()       # pylint: disable=protected-access

        if schematic:
            self._node.remove(schematic)

        return xml


    #--------------------------------------------------------------------------
    # Create Definition
    #--------------------------------------------------------------------------
    def create_definition(self, prj: "Project") -> "Definition":
        """
        Create the definition in the given project.

        Once the desired ports, graphics, and form parameters & categories
        have been added to the wizard, this method will create the required
        component definition in the given project, which may then be used
        to create instances of the component.

        .. note::
            The definition name configured in the wizard is only a hint.
            When PSCAD creates the definition, it may change the definition
            name, so refer the returned definition for the actualy definition
            name.
        """

        xml = self._xml()
        return prj.create_definition(xml)


#===============================================================================
# Typing requires complete types at the end of the module
#===============================================================================

# pylint: disable=wrong-import-order, wrong-import-position, ungrouped-imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .definition import Definition
    from .project import Project
