from typing import List, Optional

import pydantic

from classiq.interface.generator import function_params
from classiq.interface.generator.standard_gates.standard_angle_metaclass import (
    MyMetaAngledClassModel,
)

"""
To add new standard gates, refer to the following guide
https://docs.google.com/document/d/1Nt9frxnPkSn8swNpOQ983E95eaEiDWaiuWAKglGtUAA/edit#heading=h.e9g9309bzkxt
"""


class _StandardGate(function_params.FunctionParams, metaclass=MyMetaAngledClassModel):  # type: ignore[misc]
    _name: str = ""
    _num_target_qubits: pydantic.PositiveInt = pydantic.PrivateAttr(default=1)

    _num_ctrl_qubits: Optional[pydantic.PositiveInt] = pydantic.PrivateAttr(
        default=None
    )

    _input_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_INPUT_NAME])
    _output_names = pydantic.PrivateAttr(default=[function_params.DEFAULT_OUTPUT_NAME])

    @property
    def name(self):
        # this is removing the Gate suffix from the classes name
        return self._name or self.__class__.__name__[:-4].lower()

    @property
    def num_ctrl_qubit(self):
        return self._num_ctrl_qubits

    @property
    def num_target_qubits(self):
        return self._num_target_qubits

    def __init_subclass__(cls, angles: List[str] = None, **kwargs):
        super().__init_subclass__()


class XGate(_StandardGate):
    """
    creates a X gate
    """


class YGate(_StandardGate):
    """
    creates a Y gate
    """


class ZGate(_StandardGate):
    """
    create a Z gate
    """


class HGate(_StandardGate):
    """
    creates a Hadamard gate
    """


class IGate(_StandardGate):
    """
    creates the identity gate
    """

    _name: str = "id"


class SGate(_StandardGate):
    """
    Z**0.5
    """


class SdgGate(_StandardGate):
    """
    creates the inverse S gate
    """


class SXGate(_StandardGate):
    """
    X**0.5
    """


class SXdgGate(_StandardGate):
    """
    creates the inverse SX gate
    """


class TGate(_StandardGate):
    """
    Z**0.25
    """


class TdgGate(_StandardGate):
    """
    creates the inverse T gate
    """


class SwapGate(_StandardGate):
    """
    Swaps between two qubit states
    """

    _num_target_qubits: pydantic.PositiveInt = pydantic.PrivateAttr(default=2)


class iSwapGate(_StandardGate):
    """
    Swaps between two qubit states and add phase of i to the amplitudes of |01> and |10>
    """

    _num_target_qubits: pydantic.PositiveInt = pydantic.PrivateAttr(default=2)
