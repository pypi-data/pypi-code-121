"""This module defines the basic class encapsulating mode variable attributes."""
import copy
from typing import Any, Optional

from cosapp.ports.enum import Scope
from cosapp.ports.variable import BaseVariable, Types
from cosapp.utils.helpers import check_arg

import logging
logger = logging.getLogger(__name__)


class ModeVariable(BaseVariable):
    """Container for mode variables.

    Parameters
    ----------
    name : str
        Variable name
    port : ModeVarPort, optional
        Port to which the variable belongs
    value : Any
        Variable value
    unit : str, optional
        Variable unit; default empty string (i.e. dimensionless)
    dtype : type or iterable of type, optional
        Variable type; default None (i.e. type of initial value)
    desc : str, optional
        Variable description; default ''
    init : Any, optional
        Value imposed at the beginning of time simulations, if
        variable is an output (unused otherwise).
        If unspecified (default), the variable remains untouched.
    scope : Scope {PRIVATE, PROTECTED, PUBLIC}, optional
        Variable visibility; default PRIVATE
    """

    __slots__ = (
        "_init",
    )

    def __init__(
        self,
        name: str,
        port: "cosapp.ports.ModeVarPort",
        value: Optional[Any] = None,
        unit: str = "",
        dtype: Types = None,
        desc: str = "",
        init: Optional[Any] = None,
        scope: Scope = Scope.PRIVATE,
    ):
        from cosapp.ports import ModeVarPort
        from cosapp.core.eval_str import EvalString
        check_arg(port, "port", ModeVarPort)
        init = EvalString(init, port.owner)
        init_value = init.eval()
        if value is None:
            value = init_value
        elif init_value is not None:
            if not isinstance(init_value, type(value)):
                raise ValueError(
                    f"Initial value {init} appears to be inconsistent with arg value={value}."
                )

        super().__init__(name, port, value, unit, dtype, desc, scope)

        self._init = init  # type: EvalString

    def _repr_markdown_(self) -> str:
        """Returns the representation of this variable in Markdown format.

        Returns
        -------
        str
            Markdown formatted representation
        """
        msg = {"name":f"**{self.name}**" , "unit": f" {self.unit}" if self.unit else ""}
        value = self.value
        try:
            msg["value"] = f"{value:.5g}"
        except:
            msg["value"] = value

        lock_icon = "&#128274;"
        if self.description:
            msg["description"] = f" | {self.description}"
        else:
            msg["description"] = " |"

        scope_format = {
            Scope.PRIVATE: f" {lock_icon*2} ",
            Scope.PROTECTED: f" {lock_icon} ",
            Scope.PUBLIC: "",
        }
        msg["scope"] = scope_format[self.scope]

        return (
            "{name}{scope}: {value!s}{unit}"
            "{description}".format(**msg)
        )  

    @property
    def init_expr(self) -> "cosapp.core.eval_str.EvalString":
        """EvalString : expression of initial value"""
        return self._init

    def init_value(self) -> Any:
        """Evaluate and return initial value"""
        return self._init.eval()

    def initialize(self) -> None:
        """Set mode variable to its prescribed initial value."""
        value = self.init_value()
        if value is not None:
            try:
                setattr(self._port, self._name, value)
            except AttributeError:
                pass

    def copy(self, port: "BasePort", name: Optional[str] = None) -> "ModeVariable":
        if name is None:
            name = self.name
        return ModeVariable(
            name,
            value = copy.copy(self.value),
            port = port,
            unit = self._unit,
            dtype = copy.copy(self._dtype),
            desc = self._desc,
            scope = self._scope,
        )
