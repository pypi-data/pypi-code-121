# type: ignore
# We can either ignore each line individually, or ignore the entire file and wait until mypy can ignore
# specific errors per-file.
import inspect
import sys
from types import FunctionType
from typing import Any, Dict, List, Tuple, Union, _GenericAlias

from classiq.interface.generator.synthesis_metrics import MetricsRegisterRole as Role

from classiq.exceptions import ClassiqQFuncError
from classiq.quantum_register import AuxQReg, QReg, QSFixed, ZeroQReg

if sys.version_info >= (3, 9):
    from types import GenericAlias
else:
    GenericAlias = _GenericAlias

GenericAliasUnion = Union[GenericAlias, _GenericAlias]


class AnnotationParser:
    def __init__(self, func: FunctionType):
        self._func = func

        self.output_types: Dict[str, GenericAlias] = {}

    def parse(self) -> None:
        annotations = self._func.__annotations__.copy()

        # Todo: remove this `if` after introducing `Inplace`
        if "return" not in annotations:
            raise ClassiqQFuncError("Return value annotations not found")

        self.output_values = self._unpack_output_values(annotations.pop("return"))
        self.input_names, self.input_values = self._unpack_input_values(annotations)

        self._validate()

    def _validate(self) -> None:
        self._validate_type_hints()
        self._validate_qubit_amount()
        self._validate_io_length()
        self._validate_io_correlation()

    def _validate_type_hints(self) -> None:
        # Validate type of type-hints
        if not all(
            map(
                self.is_valid_generic_alias_of_qreg,
                self.input_values + self.output_values,
            )
        ):
            raise ClassiqQFuncError("Invalid GenericAlias convection")

    def _validate_qubit_amount(self) -> None:
        # Validate qubit amount
        if sum(i.size for i in self.output_values) != sum(
            i.size for i in self.input_values
        ):
            raise ClassiqQFuncError(
                "Input and output values have different amounts of qubits"
            )

    # Todo: Remove this validation by introducing better heuristics
    #   Or after introducing Inplace
    def _validate_io_length(self) -> None:
        # Validate amount of inputs and outputs
        if len(self.input_values) != len(self.output_values):
            raise ClassiqQFuncError(
                "Inputs and outputs must have the same number of QRegs"
            )

    def _validate_io_correlation(self) -> None:
        # Validate correspondence between inputs and outputs
        for input_name, input_type, output_type in zip(
            self.input_names, self.input_values, self.output_values
        ):
            # Is arithmetic QReg
            if issubclass(input_type.__origin__, QSFixed):
                if input_type != output_type:
                    raise ClassiqQFuncError(
                        f"Arithmetic QReg must be of the same type and size in both the input and the output. Got {input_type} and {output_type}"
                    )

            # Is Auxillary QReg
            if issubclass(input_type.__origin__, AuxQReg):
                if input_type != output_type:
                    raise ClassiqQFuncError(
                        f"Auxillary QReg must be of the same type and size in both the input and the output. Got {input_type} and {output_type}"
                    )

            # Is Zero QReg
            if input_type.__origin__ is ZeroQReg:
                if output_type.__origin__ is QReg or issubclass(
                    output_type.__origin__, QSFixed
                ):
                    self.output_types[input_name] = output_type
                else:
                    raise ClassiqQFuncError(
                        "Invalid output type. Any ZeroQReg in the input must have a corresponding QReg in the output"
                    )

    @classmethod
    def _unpack_output_values(
        cls, output_value_type_hint: Any
    ) -> Tuple[GenericAlias, ...]:
        # Handle QReg type hints
        if cls.is_subclass_qreg(output_value_type_hint):
            return (cls.to_generic_alias(output_value_type_hint),)

        # Supporting both `typing._GenericAlias` and `types.GenericAlias`
        if not cls.is_instance_generic_alias(output_value_type_hint):
            raise ClassiqQFuncError(
                "Output value type hint must be either a single QReg, `typing.Tuple[QReg, ...]` or, for python>=3.9, `tuple[QReg, ...]`"
            )

        # Allowing only a tuple of outputs:
        if not cls.is_tuple_generic_alias(output_value_type_hint):
            raise ClassiqQFuncError(
                "Output value type hint must be either Tuple[QReg, ...] or tuple[QReg, ...]"
            )

        # This line may raise ClassiqQFuncError
        return tuple(map(cls.to_generic_alias, output_value_type_hint.__args__))

    def _unpack_input_values(
        self, annotations: Dict[str, Any]
    ) -> Tuple[List[str], Tuple[GenericAlias, ...]]:
        input_names = list(annotations.keys())
        input_values = tuple(map(self.to_generic_alias, annotations.values()))
        return input_names, input_values

    @staticmethod
    def to_generic_alias(obj: Any) -> GenericAlias:
        # Handle GenericAlias
        if isinstance(obj, GenericAlias):
            return obj
        # Handle _GenericAlias, for python>3.9, i.e. when GenericAlias != _GenericAlias
        if isinstance(obj, _GenericAlias):
            return GenericAlias(obj.__origin__, obj.__args__)
        # Handle a single QReg (not GenericAlias of QReg)
        elif inspect.isclass(obj) and issubclass(obj, QReg):
            return GenericAlias(obj, tuple())

        raise ClassiqQFuncError(f"Invalid type hint object: {obj.__class__.__name__}")

    @staticmethod
    def is_instance_generic_alias(obj: Any) -> bool:
        return isinstance(obj, (GenericAlias, _GenericAlias))

    @classmethod
    def is_subclass_qreg(cls, obj: Any) -> bool:
        if inspect.isclass(obj):
            return issubclass(obj, QReg)
        elif cls.is_instance_generic_alias(obj):
            return issubclass(obj.__origin__, QReg)
        return False

    @staticmethod
    def is_tuple_generic_alias(obj: GenericAliasUnion) -> bool:
        return obj.__origin__.__name__.lower() == "tuple"

    @staticmethod
    def is_valid_generic_alias_of_qreg(obj: GenericAlias) -> bool:
        return (
            isinstance(obj, GenericAlias)
            and issubclass(obj.__origin__, QReg)
            and type(obj.__args__) is tuple
            # The tests below this comment force annotations with size
            and len(obj.__args__) == 1
            and type(obj.__args__[0]) is int
        )


def get_annotation_role(annotation: GenericAlias, default_role: Role) -> Role:
    """
    Note: this function cannot distinguish between inputs and outputs.
        Thus, for inputs, all 3 options are valid
        However, for outputs:
            a) we don't expect to get ZERO
            b) We treat INPUT as OUTPUT
    """
    ret = None

    if getattr(annotation, "role", None) is not None:
        ret = annotation.role
    if getattr(annotation.__origin__, "role", None) is not None:
        ret = annotation.role

    if issubclass(annotation.__origin__, QReg) and not issubclass(
        annotation.__origin__, ZeroQReg
    ):
        ret = default_role

    if issubclass(annotation.__origin__, ZeroQReg) and not issubclass(
        annotation.__origin__, AuxQReg
    ):
        ret = Role.ZERO

    if issubclass(annotation.__origin__, AuxQReg):
        ret = Role.AUXILIARY

    # Didn't match anything so far
    if ret is None:
        raise ClassiqQFuncError("Invalid annotation role")

    if default_role == Role.INPUT and ret == Role.OUTPUT:
        raise ClassiqQFuncError("input should not have Role.OUTPUT")

    if default_role == Role.OUTPUT and ret in (Role.ZERO, Role.INPUT):
        raise ClassiqQFuncError("output should not have Role.ZERO / Role.INPUT")

    return ret
