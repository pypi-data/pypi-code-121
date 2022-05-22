from typing import Any, Dict, Optional, cast

import pydantic

from classiq.interface.generator.arith.register_user_input import RegisterUserInput

_DEFAULT_CONTROL_NAME: str = "ctrl"


class ControlState(pydantic.BaseModel):
    num_ctrl_qubits: Optional[pydantic.NonNegativeInt] = pydantic.Field(
        default=None, description="The number of control qubits."
    )
    ctrl_state: Optional[str] = pydantic.Field(
        default=None, description="string of the control state"
    )
    name: str = pydantic.Field(default=_DEFAULT_CONTROL_NAME)

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

        cls._validate_control_string(ctrl_state)
        if len(ctrl_state) != num_ctrl_qubits:
            raise ValueError(
                "control state length should be equal to the number of control qubits"
            )

        return values

    @classmethod
    def _validate_control_string(cls, ctrl_state: str) -> None:
        if not set(ctrl_state) <= {"1", "0"}:
            raise ValueError(
                f"Control state can only be constructed from 0 and 1, received: {ctrl_state}"
            )

    def is_controlled(self) -> bool:
        return self.num_ctrl_qubits != 0

    def __str__(self) -> str:
        return self.ctrl_state  # type: ignore[return-value]

    def __len__(self) -> int:
        return self.num_ctrl_qubits  # type: ignore[return-value]

    @property
    def control_register(self) -> RegisterUserInput:
        return RegisterUserInput(name=self.name, size=self.num_ctrl_qubits)
