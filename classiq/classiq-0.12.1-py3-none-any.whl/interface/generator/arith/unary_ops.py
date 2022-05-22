from typing import Optional

import pydantic

from classiq.interface.generator.arith.arithmetic import DEFAULT_ARG_NAME
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import FunctionParams


class UnaryOpParams(FunctionParams):
    arg: RegisterUserInput
    output_size: Optional[pydantic.PositiveInt]
    output_name: str
    inplace: bool = False

    def _create_io_names(self):
        output_names = [self.output_name]
        arg_name = self.arg.name if self.arg.name else DEFAULT_ARG_NAME

        if not self.inplace:
            output_names.append(arg_name)

        self._output_names = output_names
        self._input_names = [arg_name]

    class Config:
        arbitrary_types_allowed = True


class BitwiseInvert(UnaryOpParams):
    output_name: str = "inverted"
    pass


class Negation(UnaryOpParams):
    output_name: str = "negated"
    pass
