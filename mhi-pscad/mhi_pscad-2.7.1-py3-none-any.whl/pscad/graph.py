#===============================================================================
# PSCAD Graph Components
#===============================================================================

"""
================
Graph Components
================
"""

#===============================================================================
# Imports
#===============================================================================

import logging
from typing import Dict, List, Optional, Tuple, Union

from .remote import rmi, rmi_property, deprecated

from .component import ZComponent
from .component import MovableMixin, CommandMixin, ParameterMixin, SizeableMixin
from .form import FormCodec
from .types import Parameters


#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# PSCAD Graph Mix-ins
#===============================================================================

#-------------------------------------------------------------------------------
# Frame Mixin - Movable, Resizable Object with titlebar, minimize/restore btns
#-------------------------------------------------------------------------------

class FrameMixin(MovableMixin, SizeableMixin, ParameterMixin):
    """
    Frames, which are movable, sizeable, and have parameters
    """


    #---------------------------------------------------------------------------
    # Titlebar
    #---------------------------------------------------------------------------

    @property
    def title(self) -> str:
        """The title displayed on the frame"""
        return self['title']

    @title.setter
    def title(self, title: str):
        self['title'] = title


    #---------------------------------------------------------------------------
    # Minimize/Restore
    #---------------------------------------------------------------------------

    @rmi
    def _minimize(self, flag):
        pass

    def minimize(self, flag: bool = True) -> None:
        """
        Minimize the frame.
        """
        self._minimize(flag)

    def restore(self) -> None:
        """
        Restore the frame from its minimized state.
        """
        self.minimize(False)

    def toggle_minimize(self) -> None:
        """
        Toggle minimized/restored state
        """
        self._minimize(-1)


#-------------------------------------------------------------------------------
# Panel Mixin - Object contains 1 or more panels
#-------------------------------------------------------------------------------

class PanelMixin:
    """
    Things with multiple panels
    """

    @rmi
    def panels(self) -> List["GraphPanel"]:
        """
        List of panels in contained in this frame
        """

    def panel(self, idx: int) -> "GraphPanel":
        """
        Retrieve the indexed panel contained in the frame.

        Parameters:
            idx (int): Panel index (zero based)
        """
        return self.panels()[idx]


#-------------------------------------------------------------------------------
# Zoom Mixin - Can zoom object
#-------------------------------------------------------------------------------

class ZoomMixin(CommandMixin):
    """
    Zoom X/Y/In/Out/Extents/Limits/Previous/Next
    """

    #---------------------------------------------------------------------------
    # Zoom Extents (current range of data in x/y axis)
    #---------------------------------------------------------------------------

    def reset_extents(self) -> None:
        """
        Reset the graph's extents
        """
        self._command('GRAPHS_ZOOM_EXTENTSALL')

    def zoom_extents(self, x_extents: bool = True, y_extents: bool = True
                     ) -> None:
        """
        Reset the graph's zoom to the X and/or Y extents.
        By default, both X and Y axis zoom is affected.

        Parameters:
            x_extents (bool): set to False to not affect X-axis
            y_extents (bool): set to False to not affect Y-axis
        """

        if x_extents and y_extents:
            self.reset_extents()
        elif x_extents:
            self.zoom_x_extents()
        elif y_extents:
            self.zoom_y_extents()
        else:
            raise ValueError("At least one axis must be selected")

    def zoom_x_extents(self) -> None:
        """
        Reset the graph's zoom for the X-axis to the X extents.
        """
        self._command('GRAPHS_ZOOM_EXTENTSX')

    def zoom_y_extents(self) -> None:
        """
        Reset the graph's zoom for the Y-axis to the Y extents.
        """
        self._command('GRAPHS_ZOOM_EXTENTSY')

    #---------------------------------------------------------------------------
    # Zoom Limits (entire range of data in x/y axis)
    # Includes simultation end-time even if yet reached
    #---------------------------------------------------------------------------

    def reset_limits(self) -> None:
        """
        Reset the graph's limits
        """
        self._command('GRAPHS_ZOOM_LIMITALL')

    def zoom_limits(self, x_limits: bool = True, y_limits: bool = True
                    ) -> None:
        """
        Reset the graph's zoom to the X and/or Y limits.
        By default, both X and Y axis zoom is affected.

        Parameters:
            x_limits (bool): set to False to not affect X-axis
            y_limits (bool): set to False to not affect Y-axis
        """

        if x_limits and y_limits:
            self.reset_limits()
        elif x_limits:
            self.zoom_x_limits()
        elif y_limits:
            self.zoom_y_limits()
        else:
            raise ValueError("At least one axis must be selected")

    def zoom_x_limits(self) -> None:
        """
        Reset the graph's zoom for the X-axis to the X limits.
        """
        self._command('GRAPHS_ZOOM_LIMITX')

    def zoom_y_limits(self) -> None:
        """
        Reset the graph's zoom for the Y-axis to the Y limits.
        """
        self._command('GRAPHS_ZOOM_LIMITY')


    #---------------------------------------------------------------------------
    # Zoom
    #---------------------------------------------------------------------------

    @rmi
    def zoom(self,
             xmin: float = None, xmax: float = None,
             ymin: float = None, ymax: float = None, *,
             compute_x_grid: bool = True, compute_y_grid: bool = True) -> None:
        """
        Set the horizontal and/or vertical limits of the overlay graph.

        All parameters are optional.

        Parameters:
            xmin (float): Lower X-Axis limit
            xmax (float): Upper X-Axis limit
            ymin (float): Lower Y-Axis limit
            ymax (float): Upper Y-Axis limit
            compute_x_grid (bool): Recompute x-grid spacing
            compute_x_grid (bool): Recompute y-grid spacing
        """

    def zoom_in(self) -> None:
        """
        Increase the graph's zoom level.
        """
        self._command('GRAPHS_ZOOM_IN')

    def zoom_out(self) -> None:
        """
        Decrease the graph's zoom level.
        """
        self._command('GRAPHS_ZOOM_OUT')

    def zoom_previous(self) -> None:
        """
        Undo zoom.
        """
        self._command('GRAPHS_ZOOM_PREV')

    def zoom_next(self) -> None:
        """
        Redo zoom.
        """
        self._command('GRAPHS_ZOOM_NEXT')

#-------------------------------------------------------------------------------
# Preferences Mixin - Grid lines, tick marks, glyphs, ...
#-------------------------------------------------------------------------------

class PreferencesMixin:
    """
    Grid line, tick marks, glyphs, and X/Y intercept preferences
    """

    grid = rmi_property(True, True, name='grid',
                        doc='Show/hide grid')
    ticks = rmi_property(True, True, name='ticks',
                         doc='Show/hide axis tick marks')
    glyphs = rmi_property(True, True, name='glyphs',
                          doc='Show/hide curve glyphs')
    x_intercept = rmi_property(True, True, name='x_intercept',
                               doc='Show/hide x-intercept')
    y_intercept = rmi_property(True, True, name='y_intercept',
                               doc='Show/hide y-intercept')

    #---------------------------------------------------------------------------
    # Grid Lines
    #---------------------------------------------------------------------------

    def show_grid(self, show: bool = True) -> None:
        """
        Set the grid visibility

        Parameters:
            show (bool): Set to ``False`` to turn off the grid.
        """
        self.grid = show

    def toggle_grid_lines(self) -> None:
        """
        Toggle grid lines on or off
        """
        self.grid = not self.grid

    #---------------------------------------------------------------------------
    # Tick Marks
    #---------------------------------------------------------------------------

    def show_ticks(self, show: bool = True) -> None:
        """
        Set the tick visibility.

        Parameters:
            show (bool): Set to ``False`` to turn off the tick markers.
        """
        self.ticks = show

    def toggle_tick_marks(self) -> None:
        """
        Toggle tick marks on or off
        """
        self.ticks = not self.ticks

    #---------------------------------------------------------------------------
    # Curve Glyphs
    #---------------------------------------------------------------------------

    def show_glyphs(self, show: bool = True) -> None:
        """
        Set the curve glyph visibility.

        Parameters:
            show (bool): Set to ``False`` to turn off the curve glyphs.
        """
        self.glyphs = show

    def toggle_curve_glyphs(self) -> None:
        """
        Toggle curve glyphs on or off
        """
        self.glyphs = not self.glyphs

    #---------------------------------------------------------------------------
    # X/Y Intercepts
    #---------------------------------------------------------------------------

    def show_x_intercept(self, show: bool = True):
        """
        Set the X intercept visibility on or off
        """
        self.x_intercept = show

    def show_y_intercept(self, show: bool = True) -> None:
        """
        Set the Y intercept visibility on or off
        """
        self.y_intercept = show

    def toggle_x_intercept(self) -> None:
        """
        Toggle X intercept on or off
        """
        self.x_intercept = not self.x_intercept

    def toggle_y_intercept(self) -> None:
        """
        Toggle Y intercept on or off
        """
        self.y_intercept = not self.y_intercept


#===============================================================================
# PSCAD Graph Frame
#===============================================================================

class GraphFrame(ZComponent, FrameMixin, PanelMixin, ZoomMixin,
                 PreferencesMixin):
    """
    A container for holding one or more overlay graphs.

    The Graph Frame parameters holds a set of properties
    for the frame itself.

    .. table:: Graph Frame Properties

       ============ ===== ============================================
       Param Name   Type  Description
       ============ ===== ============================================
       title        str   Caption of Graph Frame
       markers      bool  Show Markers
       lockmarkers  bool  Lock distance between X & O markers
       deltareadout bool  Show "Delta T" readout
       xmarker      float The X-Marker position
       omarker      float The O-Marker position
       pan_enable   bool  Auto Pan X-Axis enabled
       pan_amount   int   Auto Pan X-Axis percentage
       xtitle       str   Title of the x-axis
       xgrid        float X-Axis grid line spacing
       xfont        str   X-Axis font
       xangle       int   X-Axis label angle (in degrees)
       ============ ===== ============================================
    """

    #---------------------------------------------------------------------------
    # Parameters
    #---------------------------------------------------------------------------

    def _param_codec(self):
        return FormCodec.graph_frame(self)


    #===========================================================================
    # Toggle properties
    #===========================================================================

    markers = rmi_property(True, True, name='markers',
                           doc='Show/hide X/O markers')
    auto_sizing = rmi_property(True, True, name='auto_sizing',
                               doc='Enable/disable vertical auto sizing')
    follow_run = rmi_property(True, True, name='follow_run',
                              doc='Enable/disable auto pan (follow end of run)')

    #===========================================================================
    # Zoom (X-Axis only)
    #===========================================================================

    def zoom(self, xmin: float = None, xmax: float = None, *, # pylint: disable=arguments-differ
             compute_x_grid: bool = True) -> None:
        """
        Alter the graph's X-Axis extents
        """
        panel = self.panel(0)

        args = {}
        if xmin is not None:
            args['xmin'] = xmin
        if xmax is not None:
            args['xmax'] = xmax

        panel.zoom(**args, compute_x_grid=compute_x_grid)

    @rmi
    def _pan(self, left, right):
        pass

    def pan(self, left: float = None, right: float = None, *,
            width: float = None) -> None:
        """
        Set the location of the graph's panning bar.
        """
        if left is not None and (left < 0.0 or left >= 1.0):
            raise ValueError("Left limit out of range")
        if right is not None and (right <= 0.0 or right > 1.0):
            raise ValueError("Right limit out of range")
        if width is not None and (width <= 0.0 or width > 1.0):
            raise ValueError("Width out of range")
        if left is not None and right is not None and width is not None:
            raise ValueError("Over specified")

        if width:
            if left is not None:
                right = left + width
            elif right is not None:
                left = right - width
            else:
                left = (1.0 - width) / 2
                right = left + width

        if left is None or left < 0.0:
            left = 0.0
        if right is None or right > 1.0:
            right = 1.0

        self._pan(left, right)


    #===========================================================================
    # Panels
    #===========================================================================

    #---------------------------------------------------------------------------
    # Add Panel (Overlay Graph, Stacked Polygraph
    #---------------------------------------------------------------------------

    @rmi
    def _add_overlay_graph(self):
        pass

    def add_overlay_graph(self, *sources: Union["Curve", "PGB"]
                          ) -> Tuple["OverlayGraph", List["Curve"]]:
        """
        Add a new Overlay Graph

        Parameters:
            *sources: pgbs or curves to add to newly created graph (optional)

        Returns:
            Tuple[OverlayGraph,List[Curve]]: The new Overlay Graph & its curves
        """

        graph = self._add_overlay_graph()
        curves = graph.create_curves(*sources)

        return graph, curves

    @rmi
    def _add_poly_graph(self):
        pass

    def add_poly_graph(self, *sources: Union["Curve", "PGB"],
                       digital: bool = False
                       ) -> Tuple["PolyGraph", List["Curve"]]:
        """
        Add a new Stacked PolyGraph

        Parameters:
            *sources: pgbs or curves to add to newly created graph (optional)

        Returns:
            Tuple[PolyGraph,List[Curve]]: The new PolyGraph & its curves
            Newly added Stacked Polygraph
        """

        graph = self._add_poly_graph()
        curves = graph.create_curves(*sources, digital=digital)

        return graph, curves


    #---------------------------------------------------------------------------
    # Remove graph panels
    #---------------------------------------------------------------------------

    @rmi
    def remove(self, *panels: "GraphPanel") -> None:
        """
        Remove one or more graph panels from the Graph Frame
        """


    #---------------------------------------------------------------------------
    # Old API names
    #---------------------------------------------------------------------------

    @deprecated("Use zoom_x_extents()")
    def reset_x_axis(self):         # pylint: disable=missing-function-docstring
        return self.zoom_x_extents()

    @deprecated("Use zoom_y_extents()")
    def reset_y_axis(self):         # pylint: disable=missing-function-docstring
        return self.zoom_y_extents()

    @deprecated("Use Canvas.component(iid) or Project.component(iid)")
    def overlay_graph(self, iid):   # pylint: disable=missing-function-docstring
        return self.project().component(iid)


    #---------------------------------------------------------------------------
    # Auto-Pan
    #---------------------------------------------------------------------------

    def toggle_auto_pan(self) -> None:
        """
        Toggle auto-pan on or off.
        """
        self.follow_run = not self.follow_run

    def set_auto_pan(self, enable: bool = True) -> None:
        """
        Set auto-pan on or off.
        """
        self.follow_run = enable


    #---------------------------------------------------------------------------
    # Markers
    #---------------------------------------------------------------------------

    def toggle_markers(self) -> None:
        """
        Toggle the markers on or off.
        """
        self.markers = not self.markers

    def show_markers(self, show: bool = True) -> None:
        """
        Set the marker visibility to on or off.
        """
        self.markers = show


    #---------------------------------------------------------------------------
    # Automatic Vertical Sizing
    #---------------------------------------------------------------------------

    def toggle_auto_sizing(self) -> None:
        """
        Toggle auto-sizing on or off.
        """
        self.auto_sizing = not self.auto_sizing

    def set_auto_sizing(self, enable: bool = True) -> None:
        """
        Set auto-sizing on or off.
        """
        self.auto_sizing = enable


    #---------------------------------------------------------------------------
    # Minimize/Restore
    #---------------------------------------------------------------------------

    @rmi
    def _minimize(self, flag):
        pass

    def minimize(self, flag: bool = True) -> None:
        """
        Minimize the frame.
        """
        self._minimize(flag)

    def restore(self):
        """
        Restore the frame from its minimized state.
        """
        self.minimize(False)

    def toggle_minimize(self) -> None:
        """
        Toggle minimized/restored state
        """
        self._minimize(-1)


    #---------------------------------------------------------------------------
    # Channel Limits
    #---------------------------------------------------------------------------

    def synchronize_channel_limits(self) -> None:
        """
        Set the limits of each channel in the frame to the limits of its graph.
        """
        self._command_id(156)


    #---------------------------------------------------------------------------
    # Clipboard
    #---------------------------------------------------------------------------

    def copy(self, *graphs):        # pylint: disable=missing-function-docstring
        raise NotImplementedError()

    def cut(self, *graphs):         # pylint: disable=missing-function-docstring
        raise NotImplementedError()

    def paste(self):                # pylint: disable=missing-function-docstring
        raise NotImplementedError()


#===============================================================================
# PSCAD GraphPanel (Overlay Graph, Poly Graph, ...
#===============================================================================

class GraphPanel(ZComponent, ZoomMixin):
    """
    Graph Panel

    Parent class of OverlayGraph, PolyGraph, ...
    """

    #===========================================================================
    # Toggle properties
    #===========================================================================

    grid = rmi_property(True, True, name='grid',
                        doc='Show / hide grid')
    ticks = rmi_property(True, True, name='ticks',
                         doc='Show / hide axis tick marks')
    glyphs = rmi_property(True, True, name='glyphs',
                          doc='Show / hide curve glyphs')
    crosshair = rmi_property(True, True, name='crosshair',
                             doc='Show / hide crosshair')
    x_intercept = rmi_property(True, True, name='x_intercept',
                               doc='Show / hide x-intercept')
    y_intercept = rmi_property(True, True, name='y_intercept',
                               doc='Show / hide y-intercept')


    #---------------------------------------------------------------------------
    # Crosshairs
    #---------------------------------------------------------------------------

    def toggle_crosshair(self) -> None:
        """
        Toggle crosshair on or off.
        """
        self.crosshair = not self.crosshair

    def show_crosshair(self, show: bool = True) -> None:
        """
        Set the crosshair visibility on or off.
        """
        self.crosshair = show


    #---------------------------------------------------------------------------
    # Vertical Order
    #---------------------------------------------------------------------------

    def to_top(self) -> None:
        """
        Put at the top of the graph frame.
        """
        self._command('IDZ_CMP_FIRST')

    def move_up(self) -> None:
        """
        Move the graph one position up in the graph frame.
        """
        self._command('IDZ_CMP_PREV')

    def move_down(self) -> None:
        """
        Move the graph one position down in the graph frame.
        """
        self._command('IDZ_CMP_NEXT')

    def to_bottom(self) -> None:
        """
        Put at the bottom of the graph frame.
        """
        self._command('IDZ_CMP_LAST')

    #---------------------------------------------------------------------------
    # Copy Data
    #---------------------------------------------------------------------------

    def copy_data_all(self) -> None:
        """
        Copy all data in the graph to the clipboard.
        """
        self._command('GRAPHS_COPYDATA_ALL')

    def copy_data_visible(self) -> None:
        """
        Copy visible data in the graph to the clipboard.
        """
        self._command('GRAPHS_COPYDATA_VIS')

    def copy_data_between_markers(self) -> None:
        """
        Copy data between the markers in the graph to the clipboard.
        """
        self._command_id(902)


    #---------------------------------------------------------------------------
    # Clipboard
    #---------------------------------------------------------------------------

    def copy(self, *curves):        # pylint: disable=missing-function-docstring
        raise NotImplementedError()

    def cut(self, *curves):         # pylint: disable=missing-function-docstring
        raise NotImplementedError()

    def paste(self):
        """
        Paste contents of the clipboard
        """

        self._command('IDZ_CMP_PASTE')


    #---------------------------------------------------------------------------
    # Curves
    #---------------------------------------------------------------------------

    @rmi
    def _curves(self):
        pass

    def curves(self) -> List["Curve"]:
        """
        Retrieve the curves that belong to this graph panel.

        Returns:
            List[Curve]: the curves in this panel
        """

        return self._curves()

    @rmi
    def _curve(self, index):
        pass

    def curve(self, index: int) -> "Curve":
        """
        Retrieve a curve that belongs to this graph panel.

        Parameters:
            index (int): The curve index, starting from 0

        Returns:
            Curve: the indexed curve in this panel
        """

        return self._curve(index)

    #---------------------------------------------------------------------------
    # Create Curve
    #---------------------------------------------------------------------------

    @rmi
    def _create_curve(self, source, index):
        pass

    def create_curve(self, source: Union["PGB", "Curve"],
                     index: int = -1) -> "Curve":
        """
        Create a new curve on this graph from the given source.

        If the source is another curve, that curve is cloned.

        Parameters:
            source: The signal source (pgb or a curve)
            index: Position in graph (optional)

        Returns:
            Curve: The created curve
        """

        return self._create_curve(source, index)

    def create_curves(self, *sources: Union["PGB", "Curve"]
                      ) -> List["Curve"]:
        """
        Create new curves on this graph from the given sources.

        If a source is another curve, that curve is cloned.

        Parameters:
            *sources: The signal sources (pgbs or a curves)

        Returns:
            List[Curve]: The created curves
        """

        return [self.create_curve(source) for source in sources]

    @rmi
    def _move_curve(self, curve, index):
        pass

    def move_curve(self, curve: "Curve", index: int = -1):
        """
        Move a curve to a given position on this graph.

        If a curve is on a different graph, it is removed from that graph,
        and added to this one.

        Parameters:
            source: The signal source (pgb or a curve)
            index: Position in graph (optional)
        """
        return self._move_curve(curve, index)


#===============================================================================
# PSCAD Overlay Graph
#===============================================================================

class OverlayGraph(GraphPanel, ZoomMixin, PreferencesMixin):
    """
    Overlay Graph

    A graph object that may be contained in a graph frame.
    Inherits from :class:`.GraphPanel`.
    """

    #---------------------------------------------------------------------------
    # Parameters
    #---------------------------------------------------------------------------

    def _param_codec(self):
        return FormCodec.overlay_graph(self)

    def parameters(self, parameters: Parameters = None, # pylint: disable=arguments-differ
                   **kwargs) -> Optional[Parameters]:
        """
        Get/set Overlay Graph Settings

        .. table:: Overlay Graph Settings

           ============== ====== ==============================================
           Param Name     Type   Description
           ============== ====== ==============================================
           glyphs         bool   Glyphs
           grid           bool   Grids
           grid_color     Color  Grid Line Colour
           curve_colours  Colors Curve Colour Pattern
           curve_colours2 Colors Curve Inverted Colour Pattern
           ticks          bool   Ticks
           yinter         bool   Y-Intercept
           xinter         bool   X-Intercept
           crosshair      bool   Crosshair
           manualscale    bool   Manual Scalling Only
           invertcolor    bool   Invert Colours
           title          Text   Y-Axis Title
           gridvalue      Real   Grid Size
           ymin           Real   Minimum Value
           ymax           Real   Maximum Value
           yintervalue    Real   Intercept Value
           autoframe      Real   Padding
           ============== ====== ==============================================
        """
        return super().parameters(parameters=parameters, **kwargs)


    #===========================================================================
    # Properties
    #===========================================================================

    height = rmi_property(True, True, name='height', doc='Manual graph height')


    #===========================================================================
    # set_zoom
    #===========================================================================

    @deprecated("Use overlay_graph.zoom()")
    def set_zoom(self, xmin=None, xmax=None, ymin=None, ymax=None):
        """
        Set the horizontal and vertical limits of the overlay graph.

        Parameters:
            xmin (float): Lower X-Axis limit
            xmax (float): Upper X-Axis limit
            ymin (float): Lower Y-Axis limit
            ymax (float): Upper Y-Axis limit
        """

        compute_x_grid = xmin is not None and xmax is not None
        compute_y_grid = ymin is not None and ymax is not None
        self.zoom(xmin, xmax, ymin, ymax, compute_x_grid=compute_x_grid,
                  compute_y_grid=compute_y_grid)

    #---------------------------------------------------------------------------
    # Channel Limits
    #---------------------------------------------------------------------------

    def synchronize_channel_limits(self) -> None:
        """
        Set the limits of each channel to the limits of the graph.
        """
        self._command_id(1000)



#===============================================================================
# PSCAD PolyGraph
#===============================================================================

class PolyGraph(GraphPanel, ZoomMixin, PreferencesMixin):
    """
    Polygraph

    A graph object that may be contained in a graph frame, used to display
    strips of analog and digital traces.

    Inherits from :class:`.GraphPanel`.
    """


    def create_curve(self, source: Union["PGB", "Curve"], index: int = -1, # pylint: disable=arguments-differ
                     digital: bool = False) -> "Curve":
        """
        Create a new curve on this polygraph from the given source.

        If the source is another curve, that curve is cloned.

        Parameters:
            source: The signal source (pgb or a curve)
            index: Position in graph (optional)
            digital: Whether curve should be displayed as a digital signal (optional)

        Returns:
            Curve: The created curve
        """

        curve = self._create_curve(source, index)
        if digital:
            curve.digital = True

        return curve

    def create_curves(self, *sources: Union["PGB", "Curve"], # pylint: disable=arguments-differ
                      digital: bool = False) -> List["Curve"]:
        """
        Create new curves on this polygraph from the given sources.

        If a source is another curve, that curve is cloned.

        Parameters:
            *sources: The signal sources (pgbs or curves)
            digital: Whether curve should be displayed as a digital signal (optional)

        Returns:
            List[Curve]: The created curves
        """

        return [self.create_curve(src, digital=digital) for src in sources]


#===============================================================================
# PSCAD Plot Frame
#===============================================================================

class PlotFrame(ZComponent, FrameMixin, ZoomMixin, PreferencesMixin):
    """
    X-Y Plot Frame

    A Graph Frame that displays an X-Y curves where both X and Y values are
    dependent on another quantity, such as time.
    """

    #---------------------------------------------------------------------------
    # Parameters
    #---------------------------------------------------------------------------

    def _param_codec(self):
        return FormCodec.plot_frame(self)

    def parameters(self, parameters: Parameters = None, **kwargs # pylint: disable=arguments-differ
                   ) -> Optional[Parameters]:
        """parameters(parameter=value, ...)
        Get/set Plot Frame Settings

        .. table:: Plot Frame Settings

           ============== ====== ===========================================
           Param Name     Type   Description
           ============== ====== ===========================================
           title          Text   Caption
           glyphs         Bool   Show Glyphs
           ticks          Bool   Show Ticks
           grid           Bool   Show Grid
           grid_color     Color  Grid Line Colour
           curve_colours  Colors Curve Colour Pattern
           curve_colours2 Colors Curve Inverted Colour Pattern
           yinter         Bool   Show Y-Intercept
           xinter         Bool   Show X-Intercept
           markers        Choice Show Markers: HIDE, SHOW
           xmarker        Real   X Marker
           omarker        Real   O Marker
           ============== ====== ===========================================
        """

        parameters = dict(parameters, **kwargs) if parameters else kwargs
        plot_type = parameters.pop('type', None)
        parameters = super().parameters(parameters=parameters)
        return parameters

    #===========================================================================
    # Toggle properties
    #===========================================================================

    grid = rmi_property(True, True, name='grid',
                        doc='Show/hide grid')
    ticks = rmi_property(True, True, name='ticks',
                         doc='Show/hide axis tick marks')
    polar = rmi_property(True, True, name='polar',
                         doc='Enable/disable polar mode')
    glyphs = rmi_property(True, True, name='glyphs',
                          doc='Show/hide curve glyphs')
    markers = rmi_property(True, True, name='markers',
                           doc='Show/hide X/O markers')
    crosshair = rmi_property(True, True, name='crosshair',
                             doc='Show/hide crosshair')
    x_intercept = rmi_property(True, True, name='x_intercept',
                               doc='Show/hide x-intercept')
    y_intercept = rmi_property(True, True, name='y_intercept',
                               doc='Show/hide y-intercept')


    #---------------------------------------------------------------------------
    # Crosshairs
    #---------------------------------------------------------------------------

    def toggle_crosshair(self) -> None:
        """
        Toggle crosshair on or off.
        """
        self.crosshair = not self.crosshair

    def show_crosshair(self, show: bool = True) -> None:
        """
        Set the crosshair visibility on or off.
        """
        self.crosshair = show


    #---------------------------------------------------------------------------
    # Zoom
    #---------------------------------------------------------------------------

    @rmi
    def zoom(self,                            # pylint: disable=arguments-differ
             xmin: float = None, xmax: float = None,
             ymin: float = None, ymax: float = None,
             start: float = None, end: float = None) -> None:
        """
        Set the horizontal, vertical, and/or aperture limits of the XY Plot.

        All parameters are optional.

        Parameters:
            xmin (float): Lower X-Axis limit
            xmax (float): Upper X-Axis limit
            ymin (float): Lower Y-Axis limit
            ymax (float): Upper Y-Axis limit
            start (float): Aperture start
            end (float): Aperture end
        """


    #---------------------------------------------------------------------------
    # Aperture
    #---------------------------------------------------------------------------

    @rmi
    def aperture(self, start: float = None, end: float = None):
        """
        Set/Get the aperture limits of the XY Plot.

        All parameters are optional.

        Parameters:
            start (float): Aperture start
            end (float): Aperture end

        Returns:
            Tuple[float, float]: The plot aperture
        """


    #---------------------------------------------------------------------------
    # Copy Data
    #---------------------------------------------------------------------------

    def copy_data_all(self) -> None:
        """
        Copy all data in the XY plot to the clipboard.
        """
        self._command('GRAPHS_COPYDATA_ALL')

    def copy_data_visible(self) -> None:
        """
        Copy all data inside the XY plot's view aperature to the clipboard.
        """
        self._command('GRAPHS_COPYDATA_VIS')


    #---------------------------------------------------------------------------
    # Curves
    #---------------------------------------------------------------------------

    @rmi
    def create_curve(self, x: Union["PGB", "Curve"],
                     y: Union["PGB", "Curve"]
                     ) -> Union[Tuple["Curve"], Tuple["Curve", "Curve"]]:
        """
        Add a curve to the XY plot.

        Parameters:
            x: The signal source for the X-axis (pgb or a curve)
            y: The signal source for the Y-axis (pgb or a curve)

        Returns:
            Union[Curve, Tuple[Curve,Curve]]: The created curve(s)

        Note:

            To plot a curve in an XY plot, both the X & Y signal sources
            are required.
            Using drag-and-drop, the X & Y signals sources are added separately,
            one at a time;
            to faciliate script recording, an ``x=`` or ``y=`` keyword argument
            is used to add the individual halves of the X & Y pairs separately.
            However, it is recommended to add both signal sources at once.

        .. versionadded:: 2.1.1
        """

    def create_curves(self, *xy: Tuple[Union["PGB", "Curve"],
                                       Union["PGB", "Curve"]]
                      ) -> List[Tuple["Curve", "Curve"]]:
        """
        Add one or more curves to the XY plot.

        Parameters:
            *xy (Tuple[X,Y]): Tuples of X/Y signal sources

        Returns:
            List[Tuple[Curve,Curve]]: The created curve tuples

        .. versionadded:: 2.1.1
        """

        return [self.create_curve(x, y) for x, y in xy]

    @rmi
    def curves(self) -> List[Tuple["Curve", "Curve"]]:
        """
        Retrieve the curves that belong to this XY Plot.

        Returns:
            List[Tuple[Curve,Curve]]: the curve pairs in this plot
        """

    @rmi
    def curve(self, index: int) -> Tuple["Curve", "Curve"]:
        """
        Retrieve a curve pair that belongs to this XY Plot.

        Parameters:
            index (int): The curve pair index, starting from 0

        Returns:
            Tuple[Curve,Curve]: the indexed curve pair in this plot
        """


#===============================================================================
# PSCAD Curve
#===============================================================================

class Curve(ZComponent):
    """
    A Curve on a graph
    """

    class _FlagSet:
        def __init__(self, prop):
            self._prop = prop
            self.__doc__ = prop.__doc__

        def __set__(self, obj, value):
            bits, flags = self._prop.__get__(obj, obj.__class__)
            if isinstance(value, (list, tuple)):
                if bits == 0:
                    bits = len(value)
                elif len(value) != bits:
                    raise ValueError("Incorrect length")
                mask = (1 << bits) - 1
                value = sum(1 << idx for idx, val in enumerate(value) if val)
                flags = (flags & ~mask) | value
            else:
                if bits == 0:
                    bits = 32
                mask = (1 << bits) - 1
                flags = flags | mask if value else flags & ~mask
            self._prop.__set__(obj, flags)

        def __get__(self, obj, objtype):
            return Curve._Bits(obj, self._prop)

    class _Bits:
        def __init__(self, obj, prop):
            self._obj = obj
            self._prop = prop

        def __getitem__(self, index):
            bits, flags = self._prop.__get__(self._obj, self._obj.__class__)
            if isinstance(index, slice):
                indices = range(*index.indices(bits))
                return [bool(flags & (1 << idx)) for idx in indices]
            if index < 0:
                index += bits
            if index == 0 or  0 <= index < bits:
                return bool(flags & (1 << index))
            raise IndexError("No such flag index")

        def __setitem__(self, index, value):
            bits, flags = self._prop.__get__(self._obj, self._obj.__class__)
            if isinstance(index, slice):
                indices = range(*index.indices(bits))
                if isinstance(value, bool):
                    mask = sum(1 << idx for idx in indices)
                    flags = flags | mask if value else flags & ~mask
                else:
                    for idx, val in zip(indices, value):
                        mask = 1 << idx
                        flags = flags | mask if val else flags & ~mask
            else:
                if index < 0:
                    index += bits
                if index == 0 or 0 <= index < bits:
                    mask = 1 << index
                    flags = flags | mask if value else flags & ~mask
                else:
                    raise IndexError("No such flag index")
            self._prop.__set__(self._obj, flags)

        def __bool__(self):
            _, flags = self._prop.__get__(self._obj, self._obj.__class__)
            return bool(flags & 1)

        def __repr__(self):
            return repr(self[:])

    @rmi_property
    def source(self):
        """
        The source of the curve (Read-only)
        """

    active = rmi_property(True, True, name="active",
                          doc="The index of the active curve trace")

    bold = _FlagSet(rmi_property(True, True, name="bold",
                                 doc="Is the curve[index] bold"))
    digital = _FlagSet(rmi_property(True, True, name="digital",
                                    doc="Is the curve[index] shown digital"))
    visible = _FlagSet(rmi_property(True, True, name="visible",
                                    doc="Is the curve[index] visible"))

    def parameters(self, parameters: Parameters = None, # pylint: disable=arguments-differ
                   **kwargs) -> Optional[Parameters]:
        return self.source.parameters(parameters=parameters, **kwargs)

    def range(self, parameter: str):
        return self.source.range(parameter)

    def to_start(self) -> None:
        """
        Put first in the list of curves in the graph.
        """
        self._command('IDZ_CMP_FIRST')

    def to_end(self) -> None:
        """
        Put last in the list of curves in the graph.
        """
        self._command('IDZ_CMP_LAST')

    @rmi
    def _samples(self):
        pass

    @rmi
    def _traces(self):
        pass

    @rmi
    def _domain(self):
        pass

    @rmi
    def _trace(self, trace_num):
        pass

    @property
    def samples(self) -> int:
        """
        The number of sample points in the curve.
        This will be zero until the project has been run.  (Read-only)

        :type: int
        """

        return self._samples()

    @property
    def traces(self) -> int:
        """
        The number of traces in the curve.
        This will be zero until the project has been run.  (Read-only)

        :type: int
        """

        return self._traces()

    def __len__(self):
        return self._traces()

    def domain(self) -> "array.array":
        """
        The domain of the curve.

        Returns:
            array.array('d'): the domain axis values
        """
        return self._domain()

    def trace(self, trace_num: int = 0) -> "array.array":
        """
        An array of sample values for the indexed trace in the curve.

        Parameters:
            trace_num (int): The trace index, starting at 0

        Returns:
            array.array('d'): the trace's sample values
        """

        return self._trace(trace_num)

    def __getitem__(self, index):
        return self._trace(index)


#===============================================================================
# Typing requires complete types at the end of the module
#===============================================================================

# pylint: disable=wrong-import-order, wrong-import-position, ungrouped-imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .component import Component, PGB
    import array
