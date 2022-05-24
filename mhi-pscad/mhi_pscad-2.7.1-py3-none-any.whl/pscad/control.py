#===============================================================================
# PSCAD Control Components
#===============================================================================

"""
==================
Control Components
==================
"""

#===============================================================================
# Imports
#===============================================================================

import logging, math
from typing import Dict, List, Optional, Tuple

from .remote import rmi, rmi_property, deprecated
from .component import ZComponent, Component
from .graph import FrameMixin

from .types import Parameters



#===============================================================================
# Logging
#===============================================================================

LOG = logging.getLogger(__name__)


#===============================================================================
# PSCAD Control Frame
#===============================================================================

class ControlFrame(ZComponent, FrameMixin):
    """
    A container for holding buttons, switches, and dials
    """

    @rmi
    def create_control(self, control_component: Component) -> "Control":
        """
        Create control in the control frame connected to the given control
        component.

        The control component must be one of the following:

        * ``master:var``,
        * ``master:var_button``,
        * ``master:var_switch``, or a
        * ``master:var_dial``

        Parameters:
            control_component (Component): the control component

        Returns:
            Control: the created control
        """

    def create_controls(self, *control_components: Component) -> List["Control"]:
        """
        Create several controls in the control frame connected to the given
        control components.

        The control components must each be one of:

        * ``master:var``,
        * ``master:var_button``,
        * ``master:var_switch``, or a
        * ``master:var_dial``

        Parameters:
            *control_components (Component): A list of control components

        Returns:
            List[Control]: the created controls
        """

        return [self.create_control(cmp) for cmp in control_components]

    @rmi
    def reset(self) -> None:
        """
        Reset all controls in the control frame
        """


#===============================================================================
# PSCAD Control
#===============================================================================

class Control(Component):
    """
    Input controls allow the user to make changes to a simulation before or
    during a run, by varying set-points, or switching inputs on or off.
    """

    @rmi_property
    def link_id(self) -> int:
        """
        Related / linked component id
        """

    @property
    def linked(self) -> Component:
        """
        Component which this control component is linked to.
        """
        return self.project().component(self.link_id)

    order = rmi_property(True, True, name='order',
                         doc="Position in Control Panel")

    def parameters(self, *, parameters: Parameters = None,
                   **kwargs) -> Optional[Parameters]:
        return self.linked.parameters(parameters=parameters, **kwargs)

    def __getitem__(self, key: str):
        return self.linked[key]

    def range(self, parameter: str):
        return self.linked.range(parameter)

    @rmi
    def _set_value(self, value):
        pass

    @deprecated("Use switch.parameters(...)")
    def set_value(self, **kwargs): # pylint: disable=missing-function-docstring
        self.parameters(**kwargs)

    @rmi
    def reset(self) -> None:
        """
        Reset the control component
        """


#===============================================================================
# PSCAD Button
#===============================================================================

class Button(Control):
    """
    A momentary contact control.

    A button will output the ``Min`` value until the user clicks the
    button, at which point it will output ``Max`` for one time-step,
    and then resume outputing ``Min``:

    .. table:: Button-specific Properties

       ============ ===== ============================================
       Param Name   Type  Description
       ============ ===== ============================================
       Min          float Button's output value when not pressed
       Max          float Button's output value when pressed
       ============ ===== ============================================
    """

    def press(self) -> None:
        """
        Press the button
        """
        self._command_id(100, action="press")

    def release(self) -> None:
        """
        Release the button
        """
        self._command_id(100, action="release")

    def click(self) -> None:
        """
        Press and release the button
        """
        self.press()
        self.release()


#===============================================================================
# PSCAD Switch
#===============================================================================

class Switch(Control):
    """
    A switch will output one of two values, depending on the position
    of the switch control:

    .. table:: Switch-specific Properties

       ============ ===== ============================================
       Param Name   Type  Description
       ============ ===== ============================================
       Max          float Output value in the "On" position
       Min          float Output value in the "Off" position
       Ton          str   Text label for the "On" position
       Toff         str   Text label for the "Off" position
       Value        str   Initial State (``"ON"`` or ``"OFF"``)
       conv         str   Convert output to the nearest integer (``"YES"`` or ``"NO"``)
       ============ ===== ============================================
    """

    def on(self) -> None:                         # pylint: disable=invalid-name
        """
        Turn the switch to the On state
        """
        self.set_state(True)

    def off(self) -> None:
        """
        Turn the switch to the Off state
        """
        self.set_state(False)

    def set_state(self, state: bool) -> None:
        """
        Set the switch to the indicated state

        Parameters:
            state (bool): ``True`` = On, ``False`` = Off
        """
        self._set_value(1 if state else 0)


#===============================================================================
# PSCAD Selector
#===============================================================================

class Selector(Control):

    """
    A switch with between 3 to 10 states.  Also known as a "Dial" or
    a "Rotary Switch".

    .. table:: Selector-specific Properties

       ============ ===== ============================================
       Param Name   Type  Description
       ============ ===== ============================================
       NDP          int   # of dial positions (3 - 10)
       Value        int   Initial dial position (1 - NDP)
       conv         str   Convert output to the nearest integer (``"YES"`` or ``"NO"``)
       LabelType    str   Appearence.  ``"INDEX"``, ``"INDEX_AND_VALUE"`` or  ``"VALUE"``
       F1           float Output value for position #1
       F2           float Output value for position #2
       F3           float Output value for position #3
       F4           float Output value for position #4
       F5           float Output value for position #5
       F6           float Output value for position #6
       F7           float Output value for position #7
       F8           float Output value for position #8
       F9           float Output value for position #9
       F10          float Output value for position #10
       ============ ===== ============================================
    """

    def position(self, position: int) -> None:
        """
        Set the selector to the given position

        Parameters:
            position (int): Desired dial position (1 to NDP)
        """
        if not position in range(1, 10+1):
            raise ValueError("Invalid selector position")

        self._set_value(position - 1)


#===============================================================================
# PSCAD Slider
#===============================================================================

class Slider(Control):
    """
    A variable input between minumum & maximum values.

    .. table:: Button-specific Properties

       ============ ===== ============================================
       Param Name   Type  Description
       ============ ===== ============================================
       Max          float Slider's maximum value
       Min          float Slider's minimum value
       Value        float Slider's initial value
       Units        str   Units to display on slider control
       Collect      str   Data collection (``"CONTINUOUS"`` or ``"ON_RELEASE"``)
       ============ ===== ============================================
    """

    def value(self, value: float) -> None:
        """
        Set the slider to the given value

        Parameters:
            value (float): Slider position value
        """
        self._set_value(value)

    def limits(self, lower: float, upper: float) -> None:
        """
        Set slider minumum and maximum limits

        Parameters:
            lower (float): Lower limit for slider
            upper (float): Upper limit for slider
        """
        if not lower < upper:
            raise ValueError("Lower limit must be less than upper limit")
        if not math.isfinite(lower) or not math.isfinite(upper):
            raise ValueError("Limits must be finite")

        self.parameters(Min=lower, Max=upper)
