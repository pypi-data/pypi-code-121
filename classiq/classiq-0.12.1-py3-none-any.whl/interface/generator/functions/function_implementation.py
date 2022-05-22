from itertools import chain
from typing import Optional, Tuple, Union

import pydantic

from classiq.interface.generator.functions.register import Register
from classiq.interface.helpers.custom_pydantic_types import pydanticNonEmptyString

RegistersStrictType = Tuple[Register, ...]
RegistersType = Union[Register, RegistersStrictType]


def to_tuple(reg_type: RegistersType) -> RegistersStrictType:
    if isinstance(reg_type, Register):
        return (reg_type,)
    else:
        return reg_type


class FunctionImplementation(pydantic.BaseModel):
    """
    Facilitates the creation of a user-defined custom function implementation
    """

    class Config:
        validate_all = True

    name: Optional[pydanticNonEmptyString] = pydantic.Field(
        default=None,
        description="The name of the custom implementation",
    )

    num_qubits_in_all_registers: Optional[pydantic.PositiveInt] = pydantic.Field(
        default=None,
        alias="_num_qubits_in_all_registers",
        description="This is a private attribute",
    )

    serialized_circuit: pydanticNonEmptyString = pydantic.Field(
        description="The QASM code of the custom function implementation",
    )

    input_registers: RegistersStrictType = pydantic.Field(
        default_factory=tuple,
        description="A tuple of input registers to the custom implementation",
    )

    output_registers: RegistersStrictType = pydantic.Field(
        description="A tuple of output registers of the custom implementation",
    )

    zero_input_registers: RegistersStrictType = pydantic.Field(
        default_factory=tuple,
        description="A tuple of zero input registers to the custom implementation",
    )

    auxiliary_registers: RegistersStrictType = pydantic.Field(
        default_factory=tuple,
        description="A tuple of auxiliary registers to the custom implementation",
    )

    @pydantic.validator(
        "input_registers",
        "output_registers",
        "zero_input_registers",
        "auxiliary_registers",
        pre=True,
        always=True,
    )
    def validate_all_registers_are_tuples(
        cls,
        registers: RegistersType,
    ) -> RegistersStrictType:
        if isinstance(registers, Register):
            return (registers,)
        return registers

    @pydantic.root_validator(skip_on_failure=True)
    def validate_ranges_of_all_registers_and_num_qubits_in_all_registers(cls, values):
        input_registers: RegistersStrictType = values.get("input_registers")
        output_registers: RegistersStrictType = values.get("output_registers")
        zero_input_registers: RegistersStrictType = values.get("zero_input_registers")
        auxiliary_registers: RegistersStrictType = values.get("auxiliary_registers")

        all_input_registers = (
            input_registers + zero_input_registers + auxiliary_registers
        )
        input_qubits = set(
            chain.from_iterable(register.qubits for register in all_input_registers)
        )
        num_qubits = len(input_qubits)
        all_qubits = set(range(num_qubits))
        if num_qubits != sum(register.width for register in all_input_registers):
            raise ValueError("The input registers must not overlap.")
        if input_qubits != all_qubits:
            raise ValueError(
                "The set of qubits contained in all registers must be consecutive."
            )

        all_output_registers = output_registers + auxiliary_registers
        output_qubits = set(
            chain.from_iterable(register.qubits for register in all_output_registers)
        )
        if len(output_qubits) != sum(
            register.width for register in all_output_registers
        ):
            raise ValueError("The output registers must not overlap.")
        if not output_qubits.issubset(all_qubits):
            raise ValueError("The input and output qubits must be mutually consistent.")

        values["num_qubits_in_all_registers"] = num_qubits

        return values

    @pydantic.validator("output_registers")
    def validate_output_registers(cls, output_registers: RegistersStrictType, values):
        if not output_registers:
            raise ValueError("The outputs of a custom function must be non-empty.")
        return output_registers

    @pydantic.validator("input_registers", "output_registers")
    def validate_io_registers_are_distinct(
        cls,
        io_registers: RegistersStrictType,
    ):
        if len(io_registers) != len({io_register.name for io_register in io_registers}):
            raise ValueError("The names of IO registers must be distinct.")
        return io_registers
