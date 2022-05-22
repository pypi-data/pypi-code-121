from typing import List, Optional, _GenericAlias  # type: ignore[attr-defined]

from classiq.interface.generator.arith.arithmetic import RegisterUserInput
from classiq.interface.generator.synthesis_metrics import MetricsRegisterRole as Role

from classiq.exceptions import ClassiqQRegError
from classiq.model_designer.wire import Wire


# This class is used for QReg, to support type-hint initialization
#   Due to the `size` property of QReg
class _GenericAliasWithSize(_GenericAlias, _root=True):  # type: ignore[call-arg]
    def __call__(self, *args, **kwargs):
        if self.size is not None:
            return super().__call__(*args, size=self.size, **kwargs)
        else:
            return super().__call__(*args, **kwargs)

    @property
    def role(self) -> Optional[Role]:
        return getattr(self.__origin__, "role", None)

    @property
    def size(self) -> Optional[int]:
        if len(self.__args__) == 1 and type(self.__args__[0]) is int:
            return self.__args__[0]
        return None


# This is a private class, whose purpose is to support slicing QuantumRegisters,
#   And to keep some link between the qubits.
class _Qubit:
    _is_available = True

    def __bool__(self) -> bool:
        return self._is_available

    def __repr__(self) -> str:
        status = "available" if self._is_available else "consumed"
        return f"{self.__class__.__name__[1:]}({status})"

    @property
    def is_available(self) -> bool:
        return self._is_available

    @property
    def is_consumed(self) -> bool:
        return not self.is_available

    def consume(self) -> None:
        if self.is_consumed:
            raise ClassiqQRegError("Qubit is already consumed")
        self._is_available = False


class QReg:
    """A Quantum Register - A logical collection of several qubits.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        size (int): The amount of qubits.

    """

    is_signed: Optional[bool] = None
    fraction_places: Optional[int] = None

    # Object initialization
    def __init__(self, size: int) -> None:
        self.size: int = size

        self._wire: Wire = Wire()

        self._available_qubits: List[_Qubit] = [_Qubit() for _ in range(self.size)]

    def __class_getitem__(cls, params):
        # Supporting python 3.7+, thus returning `typing._GenericAlias` instead of `types.GenericAlias`
        if type(params) is int:
            return _GenericAliasWithSize(cls, params, inst=True, special=False)

        raise ClassiqQRegError(f"Invalid size: {params} ; int required")

    # Exported functions
    def __len__(self) -> int:
        return self.size

    # Exported functions - Availability
    @property
    def is_available(self) -> bool:
        """bool: Checks whether this QReg is available."""
        return all(self._available_qubits)

    @property
    def is_consumed(self) -> bool:
        """bool: Checks whether this QReg is consumed."""
        return not self.is_available

    def get_available_indexes(self) -> List[int]:
        """List[int]: Returns the indexes of the qubits that are available."""
        return [index for index, value in enumerate(self._available_qubits) if value]

    def consume(self) -> None:
        # This function is for internal usage.
        if self.is_consumed:
            raise ClassiqQRegError("Cannot consume a consumed QReg")

        for qubit in self._available_qubits:
            qubit.consume()

    # Wiring
    @property
    def wire(self) -> Wire:
        """Wire: Returns the wire associated with this QReg."""
        return self._wire


# QReg with arithmetic properties
class QSFixed(QReg):
    is_signed: bool = True

    def __init__(self, size: int, fraction_places: int) -> None:
        self.fraction_places: int = fraction_places
        super().__init__(size=size)

    def to_register_user_input(self) -> RegisterUserInput:
        return RegisterUserInput(
            size=self.size,
            is_signed=self.is_signed,
            fraction_places=self.fraction_places,
        )


QFixed = QSFixed


class QUFixed(QFixed):
    is_signed: bool = False


class QSInt(QFixed):
    def __init__(self, size: int):
        super().__init__(size=size, fraction_places=0)


QInt = QSInt


class QUInt(QInt):
    is_signed: bool = False


# QReg with synthesis properties
class ZeroQReg(QReg):
    role: Role = Role.ZERO


class AuxQReg(ZeroQReg):
    role: Role = Role.AUXILIARY
