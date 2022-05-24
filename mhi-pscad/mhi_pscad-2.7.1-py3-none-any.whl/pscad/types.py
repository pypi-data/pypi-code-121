#===============================================================================
# PSCAD Automation Library Types
#===============================================================================

"""
=========
Types
=========
"""


#===============================================================================
# Imports
#===============================================================================

from enum import IntEnum
from typing import Any, Dict, List, NamedTuple, Tuple, Union


#===============================================================================
# Ports
#===============================================================================

class NodeType(IntEnum):
    """
    Node Input/Output/Electrical Type
    """

    UNKNOWN = 0
    INPUT = 1
    OUTPUT = 2
    ELECTRICAL = 3
    SHORT = 4

class Electrical(IntEnum):
    """
    Electrical Node Types
    """

    FIXED = 0
    REMOVABLE = 1
    SWITCHED = 2
    GROUND = 3

class Signal(IntEnum):
    """
    Data Signal Types
    """

    ELECTRICAL = 0
    LOGICAL = 1
    INTEGER = 2
    REAL = 3
    COMPLEX = 4
    UNKNOWN = 15

Point = NamedTuple("Point", [('x', int), ('y', int)])

Port = NamedTuple("Port", [('x', int), ('y', int), ('name', str), ('dim', int),
                           ('type', NodeType), ('electrical', Electrical),
                           ('signal', Signal)])

AnyPoint = Union[Point, Port, Tuple[int, int]]


#===============================================================================
# Graphics
#===============================================================================

class Align(IntEnum):
    """
    Text Alignment
    """

    LEFT = 0
    CENTER = 1
    RIGHT = 2

class Side(IntEnum):
    """
    Annotation Side
    """

    NONE = 0
    LEFT = 1
    TOP = 2
    RIGHT = 3
    BOTTOM = 4
    AUTO = 5

class LineStyle(IntEnum):
    """
    Line Styles
    """

    SOLID = 0
    DASH = 1
    DOT = 2
    DASHDOT = 3

class FillStyle(IntEnum):
    """
    Fill Styles
    """

    HOLLOW = 0
    SOLID = 1
    BACKWARD_DIAGONAL = 2
    FORWARD_DIAGONAL = 3
    CROSS = 4
    DIAGONAL_CROSS = 5
    HORIZONTAL = 6
    VERTICAL = 7
    GRADIENT_HORZ = 8
    GRADIENT_VERT = 9
    GRADIENT_BACK_DIAG = 10
    GRADIENT_FORE_DIAG = 11
    GRADIENT_RADIAL = 12


#===============================================================================
# Parameters
#===============================================================================

Parameters = Dict[str, Any]


#===============================================================================
# Project Type, Message
#===============================================================================

class ProjectType(IntEnum):
    """
    Project Types
    """

    CASE = 1
    LIBRARY = 2

Message = NamedTuple('Message', [('text', str),
                                 ('label', str),
                                 ('status', str),
                                 ('scope', str),
                                 ('name', str),
                                 ('link', int),
                                 ('group', int),
                                 ('classid', str)])


#===============================================================================
# Definition Views
#===============================================================================

class View(IntEnum):
    """
    View Tabs
    """

    SCHEMATIC = 1
    CIRCUIT = 1
    FORTRAN = 2
    DATA = 3
    GRAPHIC = 4
    PARAMETERS = 5
    PARAMETER = 5
    SCRIPT = 6

#===============================================================================
# Components & Aliases
#===============================================================================

BUILTIN_COMPONENTS = frozenset((
    'Bus', 'TLine', 'Cable',
    'GraphFrame', 'PlotFrame', 'ControlFrame',
    'OverlayGraph', 'PolyGraph', 'Curve',
    'Button', 'Switch', 'Selector', 'Slider',
    'Oscilloscope', 'PhasorMeter', 'PolyMeter',
    'Sticky', 'Divider',
    'BookmarkCmp', 'FileCmp', 'CaseCmp', 'UrlCmp',
    'WireOrthogonal', 'WireDiagonal',
    ))

BUILTIN_COMPONENT_ALIAS = {
    'Wire': 'WireOrthogonal',
    'StickyWire': 'WireDiagonal',
    'Bookmark': 'BookmarkCmp',
    }
