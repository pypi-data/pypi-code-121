from typing import List, Tuple

import numpy as np
import pydantic
from scipy.stats import norm

from classiq.interface.generator import function_params, linear_pauli_rotations
from classiq.interface.helpers.custom_pydantic_types import (
    pydanticNonOneProbabilityFloat,
    pydanticProbabilityFloat,
)

STATE_TARGET = linear_pauli_rotations.STATE_TARGET
RHOS_PZEROS_LENGTH_ERROR_MSG = "rhos and p_zeros must have the same length"


class LinearGCI(function_params.FunctionParams):
    """
    A circuit composed of a series of Y rotations to perform a linear approximation to the Gaussian Conditional
    Independence model.
    The model consists of a Bernoulli probability, which itself is a function of a latent random variable x:
    p(x) = F( (F_inv(p_zero) + x*sqrt(rho))/sqrt(1-rho) )
    with F being the Gaussian CDF, p_zero is p(x=0) when rho=0, and rho reflects the sensitivity.

    The circuit takes a state register |x> and zero-input target qubits.
    Each target qubit undergoes the following transformation:
    |x>|0> -> cos((slope*x + offset)/2)|x>|0> + sin((slope*x + offset)/2)|x>|1>
    Where the slope and the offset are determined by the linear approximation of the inverse sine of p(x).
    """

    _input_names = pydantic.PrivateAttr(default=STATE_TARGET)
    _output_names = pydantic.PrivateAttr(default=STATE_TARGET)

    num_state_qubits: pydantic.PositiveInt = pydantic.Field(
        description="The number of input qubits"
    )
    truncation_value: float = pydantic.Field(
        description="The truncation value of the latent normal distribution"
    )
    p_zeros: List[pydanticProbabilityFloat] = pydantic.Field(
        description="The probability when the latent normal variable equals zero"
    )
    rhos: List[pydanticNonOneProbabilityFloat] = pydantic.Field(
        "The sensitivity of the probability to changes in the latent normal variable values"
    )

    @pydantic.validator("rhos")
    def validate_rhos(cls, rhos, values):
        p_zeros = values.get("p_zeros")
        if len(p_zeros) != len(rhos):
            raise ValueError(RHOS_PZEROS_LENGTH_ERROR_MSG)
        return rhos

    @property
    def linear_pauli_rotations(self) -> linear_pauli_rotations.LinearPauliRotations:
        num_state_qubits = self.num_state_qubits
        truncation_value = self.truncation_value
        rhos = self.rhos
        p_zeros = self.p_zeros
        offsets, slopes = get_gci_values(
            num_state_qubits, truncation_value, rhos, p_zeros
        )
        num_target_qubits = len(rhos)
        bases = ["Y"] * num_target_qubits

        return linear_pauli_rotations.LinearPauliRotations(
            num_state_qubits=num_state_qubits,
            bases=bases,
            offsets=offsets,
            slopes=slopes,
        )


def get_gci_values(
    qubit_count_state: int,
    truncation_value: float,
    rhos: List[float],
    p_zeros: List[float],
) -> Tuple[List[float], List[float]]:
    qubit_count_target = len(rhos)

    # Qiskit's code below

    # get normal (inverse) CDF and pdf
    def F(x: float) -> float:
        return norm.cdf(x)

    def F_inv(x: float) -> float:
        return norm.ppf(x)

    def f(x: float) -> float:
        return norm.pdf(x)

    # create linear rotations for conditional defaults
    slopes = []
    offsets = []
    for k in range(qubit_count_target):
        psi = F_inv(p_zeros[k]) / np.sqrt(1 - rhos[k])

        # compute slope / offset
        slope = -np.sqrt(rhos[k]) / np.sqrt(1 - rhos[k])
        slope *= f(psi) / np.sqrt(1 - F(psi)) / np.sqrt(F(psi))
        offset = 2 * np.arcsin(np.sqrt(F(psi)))

        # adjust for integer to normal range mapping
        offset += slope * (-truncation_value)
        slope *= 2 * truncation_value / (2**qubit_count_state - 1)

        offsets.append(offset)
        slopes.append(slope)

    return offsets, slopes
