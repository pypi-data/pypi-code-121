from typing import List

import pydantic

from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import FunctionParams


class Identity(FunctionParams):
    arguments: List[RegisterUserInput] = pydantic.Field(
        default_factory=list, description="registers describing the state (ordered)"
    )

    @pydantic.validator("arguments")
    def _validate_argument_names(
        cls, arguments: List[RegisterUserInput]
    ) -> List[RegisterUserInput]:
        for index, arg in enumerate(arguments):
            if arg.name is None:
                arg.name = cls._get_default_arg_name(index)
        return arguments

    def _create_io_names(self) -> None:
        self._input_names: List[str] = list(arg.name for arg in self.arguments)  # type: ignore[misc]
        self._output_names: List[str] = self._input_names

    @staticmethod
    def _get_default_arg_name(index: int) -> str:
        return f"arg_{index}"
