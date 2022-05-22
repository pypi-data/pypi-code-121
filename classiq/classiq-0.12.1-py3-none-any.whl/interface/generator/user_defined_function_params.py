from typing import Set

import pydantic

from classiq.interface.generator.function_params import FunctionParams


class CustomFunction(FunctionParams):
    """
    A user-defined custom function parameters object.
    """

    name: str = pydantic.Field(description="The name of a custom function")

    def generate_io_names(self, input_set: Set[str], output_set: Set[str]):
        self._input_names = list(input_set)
        self._output_names = list(output_set)
