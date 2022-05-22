import abc
import re
from enum import Enum
from typing import Any, Iterable, List, Optional

import pydantic
from pydantic.fields import ModelPrivateAttr

from classiq.interface.generator.arith.register_user_input import RegisterUserInput

DEFAULT_OUTPUT_NAME = "OUT"
DEFAULT_INPUT_NAME = "IN"

BAD_INPUT_REGISTER_ERROR_MSG = "Bad input register name given"
BAD_OUTPUT_REGISTER_ERROR_MSG = "Bad output register name given"
END_BAD_REGISTER_ERROR_MSG = (
    "Register name must be in snake_case and begin with a letter."
)

ALPHANUM_AND_UNDERSCORE = r"[0-9a-zA-Z_]*"
NAME_REGEX = rf"[a-zA-Z]{ALPHANUM_AND_UNDERSCORE}"


class IO(Enum):
    Input = "Input"
    Output = "Output"


def input_io(is_inverse: bool) -> IO:
    if is_inverse:
        return IO.Output
    return IO.Input


def output_io(is_inverse: bool) -> IO:
    if is_inverse:
        return IO.Input
    return IO.Output


class ParamMetadata(pydantic.BaseModel):
    pass


class FunctionParams(pydantic.BaseModel, abc.ABC):
    _input_names: List[str] = pydantic.PrivateAttr(default_factory=list)
    _output_names: List[str] = pydantic.PrivateAttr(default=[DEFAULT_OUTPUT_NAME])

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._create_io_names()
        self._validate_io_names()

    def get_io_names(self, io: IO, is_inverse: bool = False) -> List[str]:
        assert io == IO.Input or io == IO.Output, "Unsupported IO type"
        if (io == IO.Input) ^ is_inverse:
            return self._input_names.copy()
        else:
            return self._output_names.copy()

    def _create_io_names(self) -> None:
        pass

    def _validate_io_names(self) -> None:
        error_msg: List[str] = []
        error_msg += self._get_error_msg(
            self._input_names, BAD_INPUT_REGISTER_ERROR_MSG
        )
        error_msg += self._get_error_msg(
            self._output_names, BAD_OUTPUT_REGISTER_ERROR_MSG
        )
        if error_msg:
            error_msg += [END_BAD_REGISTER_ERROR_MSG]
            raise ValueError("\n".join(error_msg))

    def _get_error_msg(self, names: Iterable[str], msg: str) -> List[str]:
        bad_names = [name for name in names if re.fullmatch(NAME_REGEX, name) is None]
        return [f"{msg}: {bad_names}"] if bad_names else []

    def is_valid_io_name(self, name: str, io: IO) -> bool:
        return name in self.get_io_names(io)

    @classmethod
    def get_default_input_names(cls) -> Optional[List[str]]:
        return cls._get_io_name_default_if_exists(io_attr_name="_input_names")

    @classmethod
    def get_default_output_names(cls) -> Optional[List[str]]:
        return cls._get_io_name_default_if_exists(io_attr_name="_output_names")

    @classmethod
    def _is_default_create_io_method(cls) -> bool:
        return cls._create_io_names == FunctionParams._create_io_names

    @classmethod
    def _get_io_name_default_if_exists(cls, io_attr_name: str) -> Optional[List[str]]:
        if not cls._is_default_create_io_method():
            return None

        attr: ModelPrivateAttr = cls.__private_attributes__[io_attr_name]
        return attr.get_default()

    @staticmethod
    def _assert_boolean_register(reg: RegisterUserInput) -> None:
        if reg.is_boolean_register():
            return
        raise ValueError("Register doesn't match a boolean variable")

    def get_metadata(self) -> Optional[ParamMetadata]:
        return None
