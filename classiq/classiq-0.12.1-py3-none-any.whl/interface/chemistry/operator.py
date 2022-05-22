import enum

import numpy as np
import pydantic
from more_itertools import all_equal

from classiq.interface.generator.complex_type import Complex
from classiq.interface.helpers.custom_pydantic_types import (
    pydanticPauliList,
    pydanticPauliMonomial,
    pydanticPauliMonomialStr,
)


class PauliOperator(pydantic.BaseModel):
    """
    Specification of a Pauli sum operator.
    """

    pauli_list: pydanticPauliList = pydantic.Field(
        description="A list of tuples each containing a pauli string comprised of I,X,Y,Z characters and a complex coefficient; for example [('IZ', 0.1), ('XY', 0.2)].",
    )

    def show(self) -> str:
        if self.to_hermitian():
            return "\n".join(
                f"{summand[1].real:+.3f} * {summand[0]}" for summand in self.pauli_list
            )
        return "\n".join(
            f"+({summand[1]:+.3f}) * {summand[0]}" for summand in self.pauli_list
        )

    def to_hermitian(self) -> bool:
        if not all(
            np.isclose(complex(summand[1]).real, summand[1])
            for summand in self.pauli_list
        ):
            return False
        self.pauli_list = [
            (summand[0], complex(summand[1].real)) for summand in self.pauli_list
        ]
        return True

    @pydantic.validator("pauli_list", each_item=True)
    def validate_pauli_monomials(cls, monomial):
        _PauliMonomialLengthValidator(  # type: ignore[call-arg]
            monomial=monomial
        )  # Validate the length of the monomial.
        parsed_monomial = _PauliMonomialParser(string=monomial[0], coeff=monomial[1])  # type: ignore[call-arg]
        return (parsed_monomial.string, parsed_monomial.coeff)

    @pydantic.validator("pauli_list")
    def validate_pauli_list(cls, pauli_list):
        if not all_equal(len(summand[0]) for summand in pauli_list):
            raise ValueError("Pauli strings have incompatible lengths.")
        return pauli_list

    def __mul__(self, coefficient: complex) -> "PauliOperator":
        multiplied_ising = [
            (monomial[0], monomial[1] * coefficient) for monomial in self.pauli_list
        ]
        return self.__class__(pauli_list=multiplied_ising)

    def __imul__(self, coefficient: complex) -> "PauliOperator":
        self.pauli_list = [
            (monomial[0], monomial[1] * coefficient) for monomial in self.pauli_list
        ]
        return self


# This class validates the length of a monomial.
@pydantic.dataclasses.dataclass
class _PauliMonomialLengthValidator:
    monomial: pydanticPauliMonomial


@pydantic.dataclasses.dataclass
class _PauliMonomialParser:
    string: pydanticPauliMonomialStr
    coeff: Complex


class OperatorStatus(str, enum.Enum):
    SUCCESS = "success"
    ERROR = "error"


class OperatorResult(pydantic.BaseModel):
    status: OperatorStatus
    details: PauliOperator
