from typing import List, Optional, Union

import numpy as np
import pydantic

from classiq.interface.generator import complex_type, function_params

DataNumber = Union[complex_type.Complex, float, int]
DataArray = List[List[DataNumber]]

UNITARY_GATE_INPUTS = ["IN"]
UNITARY_GATE_OUTPUTS = ["OUT"]
UNITARY_GATE_CONTROLLED_INPUTS = ["CTRL_IN", "TARGET_IN"]
UNITARY_GATE_CONTROLLED_OUTPUTS = ["CTRL_OUT", "TARGET_OUT"]


class UnitaryGate(function_params.FunctionParams):
    """
    Creates a circuit implementing a specified 2**n * 2**n unitary transformation.
    Use the num_ctrl_qubits to create a controlled unitary transformation, and the ctrl_state field to customize the
    control state.
    """

    # TODO - add support to numpy array-like (requires custom pydantic type definition)
    data: DataArray = pydantic.Field(
        description="A 2**n * 2**n (n positive integer) unitary matrix."
    )
    num_ctrl_qubits: Optional[pydantic.PositiveInt] = pydantic.Field(
        description="If specified and greater than 0, returns a num_ctrl_qubits controlled unitary gate"
    )
    ctrl_state: Optional[Union[str, pydantic.NonNegativeInt]] = pydantic.Field(
        description="The control state in decimal or as a bit string (e.g. `1011`). If not specified, the control state is 2**num_ctrl_qubits - 1"
    )

    # TODO - decide if to include assertion on the unitarity of the matrix. It is already done in Qiskit and could be computationally expensive
    @pydantic.validator("data")
    def validate_data(cls, data):
        data_np = np.array(data, dtype=object)
        if data_np.ndim != 2:
            raise ValueError("Data must me two dimensional")
        if data_np.shape[0] != data_np.shape[1]:
            raise ValueError("Matrix must be square")
        if not np.mod(np.log2(data_np.shape[0]), 1) == 0:
            raise ValueError("Matrix dimensions must be an integer exponent of 2")
        return data

    @pydantic.validator("ctrl_state")
    def validate_ctrl_state(cls, ctrl_state, values):
        num_ctrl_qubits = values.get("num_ctrl_qubits")
        if num_ctrl_qubits is None:
            return ctrl_state
        if ctrl_state is None:
            return "1" * num_ctrl_qubits
        ctrl_state_int = (
            int(ctrl_state, 2) if isinstance(ctrl_state, str) else ctrl_state
        )
        if 0 <= ctrl_state_int < 2**num_ctrl_qubits:
            return ctrl_state
        else:
            raise ValueError(
                "Control state value should be zero or positive and smaller than 2**num_ctrl_qubits"
            )

    def _create_io_names(self):
        if self.num_ctrl_qubits is None:
            self._input_names = UNITARY_GATE_INPUTS
            self._output_names = UNITARY_GATE_OUTPUTS
        else:
            self._input_names = UNITARY_GATE_CONTROLLED_INPUTS
            self._output_names = UNITARY_GATE_CONTROLLED_OUTPUTS
