# -*- coding: utf-8 -*-
from typing import TYPE_CHECKING, List

import pydantic

from classiq.interface.generator import function_params

STATE = "state"
TARGET = "target"
STATE_TARGET = [STATE, TARGET]

LENGTH_ERROR_MESSAGE = "Slopes, offsets and basis values must have the same length"

if TYPE_CHECKING:
    pydanticPauliBasisStr = str
else:
    pydanticPauliBasisStr = pydantic.constr(
        to_lower=True,
        regex=r"[xyz]",
    )


class LinearPauliRotations(function_params.FunctionParams):
    """
    Perform independent linear rotations on target qubits, each controlled by an identical
    n-qubit state register |x>.

    Each target qubit, indexed with k and denoted by q_k, undergoes the following transformation:
    |x>|q_k> -> |x> * [cos(theta(x,k)/2) + i*sin(theta(x,k)/2)*sigma]|q_k>
    with sigma being 'X', 'Y' or 'Z' Pauli matrix, and the angle is a linear function of the state,
    theta(x,k)/2 = (slope(k)*x + offset(k))/2.

    For example, a 'Y' rotation on one target qubit will result in a circuit implementing the following logic:
    |x>|0> -> cos((slope*x + offset)/2)|x>|0> + sin((slope*x + offset)/2)|x>|1>

            q_0: ─────────────────────────■───────── ... ──────────────────────
                                          │
                                          .
                                          │
        q_(n-1): ─────────────────────────┼───────── ... ───────────■──────────
                  ┌────────────┐  ┌───────┴───────┐       ┌─────────┴─────────┐
         target: ─┤ RY(offset) ├──┤ RY(2^0 slope) ├  ...  ┤ RY(2^(n-1) slope) ├
                  └────────────┘  └───────────────┘       └───────────────────┘
    """

    _input_names = pydantic.PrivateAttr(default=STATE_TARGET)
    _output_names = pydantic.PrivateAttr(default=STATE_TARGET)

    num_state_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of input qubits"
    )
    bases: List[pydanticPauliBasisStr] = pydantic.Field(
        description="The types of Pauli rotations ('X', 'Y', 'Z')."
    )
    slopes: List[float] = pydantic.Field(
        description="The slopes of the controlled rotations."
    )
    offsets: List[float] = pydantic.Field(
        description="The offsets of the controlled rotations."
    )

    @pydantic.validator("bases", "slopes", "offsets", pre=True, always=True)
    def as_list(cls, v):
        if not isinstance(v, list):
            v = [v]
        return v

    @pydantic.root_validator()
    def validate_lists(cls, values):
        offsets = values.get("offsets")
        bases = values.get("bases")
        slopes = values.get("slopes")
        if len(slopes) == len(offsets) and len(offsets) == len(bases):
            return values
        raise ValueError(LENGTH_ERROR_MESSAGE)
