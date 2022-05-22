from typing import Any, Dict, List, Optional

import pydantic

from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import FunctionParams

CTRL = "CTRL_IN"
TARGET_QUBIT = "TARGET_QUBIT"


class Mcx(FunctionParams):
    """
    multi-controlled x-gate
    """

    arguments: List[RegisterUserInput] = pydantic.Field(
        default_factory=list, description="registers describing the state (ordered)"
    )
    num_ctrl_qubits: Optional[pydantic.PositiveInt] = pydantic.Field(
        description="The number of control qubits."
    )
    ctrl_state: Optional[str] = pydantic.Field(
        default=None, description="string of the control state"
    )

    @pydantic.validator("arguments", always=True)
    def _validate_argument_names(
        cls, arguments: List[RegisterUserInput]
    ) -> List[RegisterUserInput]:
        register_name_list: List[Optional[str]] = [arg.name for arg in arguments]
        if None in register_name_list:
            raise ValueError("All registers must be named")

        if len(set(register_name_list)) != len(register_name_list):
            raise ValueError("Registers must have distinct names")

        return arguments

    @pydantic.validator("num_ctrl_qubits", always=True)
    def _validate_sizes(cls, num_ctrl_qubits: int, values: Dict[str, Any]) -> int:
        arguments_size = sum(arg.size for arg in values.get("arguments", list()))

        if not num_ctrl_qubits:
            num_ctrl_qubits = arguments_size - 1

        if num_ctrl_qubits < 1:
            raise ValueError("Must have control qubits")

        if arguments_size == 0:
            ctrl_register = RegisterUserInput(size=num_ctrl_qubits, name=CTRL)
            target_register = RegisterUserInput(size=1, name=TARGET_QUBIT)
            values["arguments"] = [ctrl_register, target_register]
        elif num_ctrl_qubits != arguments_size - 1:
            raise ValueError("Given sizes do not match")

        return num_ctrl_qubits

    @pydantic.validator("ctrl_state", always=True)
    def validate_ctrl_state(cls, ctrl_state, values):
        num_ctrl_qubits = values.get("num_ctrl_qubits")
        if ctrl_state is None:
            return "1" * num_ctrl_qubits

        if len(ctrl_state) != num_ctrl_qubits:
            raise ValueError(
                "control state length should be equal to the number of control qubits"
            )
        return ctrl_state

    def _create_io_names(self) -> None:
        names: List[str] = [getattr(arg, "name", "") for arg in self.arguments]
        self._input_names: List[str] = names
        self._output_names: List[str] = names
