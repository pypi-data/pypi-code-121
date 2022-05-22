from typing import Optional

from classiq.interface.generator.arith.arithmetic import ArithmeticOracle
from classiq.interface.generator.function_params import (
    IO,
    FunctionParams,
    ParamMetadata,
)
from classiq.interface.generator.state_preparation import StatePreparation


class GroverOperator(FunctionParams):
    oracle: ArithmeticOracle
    state_preparation: Optional[StatePreparation] = None
    diffuser: Optional[str] = None

    def _create_io_names(self) -> None:
        self._input_names = self.oracle.get_io_names(IO.Input)
        self._output_names = self.oracle.get_io_names(IO.Input)

    def get_metadata(self) -> "GroverMetadata":
        return GroverMetadata(**self.dict())

    class Config:
        extra = "forbid"


class GroverMetadata(ParamMetadata, GroverOperator):
    pass
