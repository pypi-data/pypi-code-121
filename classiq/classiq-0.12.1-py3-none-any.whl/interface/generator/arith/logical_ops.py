from typing import Any, Dict, List, Optional, Union

import pydantic

from classiq.interface.generator.arith.arithmetic import DEFAULT_ARG_NAME
from classiq.interface.generator.arith.fix_point_number import FixPointNumber
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import FunctionParams


class LogicalOps(FunctionParams):
    args: List[Union[RegisterUserInput, FixPointNumber, int, float]]
    output_name: str
    target: Optional[RegisterUserInput]

    @pydantic.validator("args")
    def validate_inputs_sizes(cls, args):
        for arg in args:
            if isinstance(arg, RegisterUserInput) and (
                arg.size != 1 or arg.fraction_places != 0
            ):
                raise ValueError(
                    f"All inputs to logical and must be of size 1 | {arg.name}"
                )
        return args

    @pydantic.validator("args")
    def set_inputs_names(cls, args):
        for i, arg in enumerate(args):
            if isinstance(arg, RegisterUserInput):
                arg.name = arg.name if arg.name else DEFAULT_ARG_NAME + str(i)
        return args

    @pydantic.validator("target", always=True)
    def _validate_target(
        cls, target: Optional[RegisterUserInput], values: Dict[str, Any]
    ) -> Optional[RegisterUserInput]:
        if target:
            cls._assert_boolean_register(target)
            target.name = target.name if target.name else values.get("output_name")
        return target

    def _create_io_names(self) -> None:
        arg_names: List[str] = [
            arg.name
            for arg in self.args
            if isinstance(arg, RegisterUserInput) and arg.name
        ]
        self._input_names: List[str] = list()
        self._input_names += arg_names
        if self.target:
            assert self.target.name, "Target must have a name"
            self._input_names += [self.target.name]
        self._output_names: List[str] = arg_names + [self.output_name]

    @staticmethod
    def _assert_boolean_register(reg: RegisterUserInput) -> None:
        if reg.is_signed or (reg.size != 1) or (reg.fraction_places != 0):
            raise ValueError("Register doesn't match a boolean variable")

    class Config:
        arbitrary_types_allowed = True


class LogicalAnd(LogicalOps):
    output_name: str = "and"
    pass


class LogicalOr(LogicalOps):
    output_name: str = "or"
    pass
