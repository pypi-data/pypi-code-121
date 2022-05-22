from typing import Any, Dict, List, Optional, cast

import pydantic

from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import FunctionParams

CTRL = "CTRL"
TARGET = "TARGET"


class Mcu(FunctionParams):
    """
    Multi-controlled u-gate.
    Based on U(theta, phi) = RZ(phi + pi/2) RX(theta) RZ(-phi - pi/2)
    For a general gate U, four angles are required - theta, phi, lambda and gamma.
    We support only some of those use cases to implement MCU using MCX and manipulation on our target qubit.

    Matrix representation:
        cos(theta / 2)              -e^{-i*phi}sin(theta / 2)
        e^{i*phi}sin(theta / 2)     cos(theta / 2)

    """

    theta: pydantic.NonNegativeFloat = pydantic.Field(
        description="Theta radian angle from U(theta, phi) = RZ(phi + pi/2) RX(theta) RZ(-phi - pi/2)."
    )
    phi: pydantic.NonNegativeFloat = pydantic.Field(
        description="Phi radian angle from U(theta, phi) = RZ(phi + pi/2) RX(theta) RZ(-phi - pi/2)."
    )

    num_ctrl_qubits: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None, description="The number of control qubits."
    )
    ctrl_state: Optional[str] = pydantic.Field(
        default=None, description="string of the control state"
    )

    _registers: List[RegisterUserInput] = pydantic.PrivateAttr()

    @pydantic.root_validator()
    def validate_control(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        num_ctrl_qubits = values.get("num_ctrl_qubits")
        ctrl_state = values.get("ctrl_state")

        if ctrl_state is not None:
            ctrl_state = cast(str, ctrl_state)

        if ctrl_state is None and num_ctrl_qubits is None:
            raise ValueError("num_ctrl_qubits or ctrl_state must exist.")

        if ctrl_state is None and num_ctrl_qubits is not None:
            values["ctrl_state"] = "1" * num_ctrl_qubits
            ctrl_state = values["ctrl_state"]

        if num_ctrl_qubits is None and ctrl_state is not None:
            num_ctrl_qubits = len(ctrl_state)
            values["num_ctrl_qubits"] = num_ctrl_qubits

        if len(ctrl_state) != num_ctrl_qubits:
            raise ValueError(
                "control state length should be equal to the number of control qubits"
            )

        return values

    def _set_registers(self) -> None:
        if self.num_ctrl_qubits is None:
            raise ValueError("num_ctrl_qubits must have a valid value.")
        ctrl_register = RegisterUserInput(size=self.num_ctrl_qubits, name=CTRL)
        target_register = RegisterUserInput(size=1, name=TARGET)
        self._registers = [ctrl_register, target_register]

    def _create_io_names(self) -> None:
        self._set_registers()
        names: List[str] = [getattr(arg, "name", "") for arg in self._registers]
        self._input_names: List[str] = names
        self._output_names: List[str] = names
