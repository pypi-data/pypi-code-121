from typing import List

import pydantic

from classiq.interface.generator.function_params import FunctionParams

_DEFAULT_RB_NAME = "rb_reg"


class RandomizedBenchmarking(FunctionParams):
    num_of_qubits: pydantic.PositiveInt
    num_of_cliffords: pydantic.PositiveInt
    register_name: str = _DEFAULT_RB_NAME

    def _create_io_names(self) -> None:
        names: List[str] = [self.register_name]
        self._input_names = names
        self._output_names = names
