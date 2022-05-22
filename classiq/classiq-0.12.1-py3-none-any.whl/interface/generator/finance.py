from typing import List, Tuple, Union

import pydantic

from classiq.interface.finance.function_input import FinanceFunctionInput
from classiq.interface.finance.model_input import FinanceModelInput
from classiq.interface.generator import function_params
from classiq.interface.generator.function_params import ParamMetadata


class Finance(function_params.FunctionParams):
    model: FinanceModelInput = pydantic.Field(description="Load a financial model")
    finance_function: Union[FinanceFunctionInput] = pydantic.Field(
        description="The finance function to solve the model"
    )

    _input_names = pydantic.PrivateAttr(default_factory=list)
    _output_names = pydantic.PrivateAttr(default=["out"])

    def get_metadata(self) -> "FinanceMetadata":
        return FinanceMetadata(**self.dict())


class FinanceMetadata(ParamMetadata, Finance):
    pass


class FinanceModelMetadata(ParamMetadata):
    num_model_qubits: int
    distribution_range: List[float]


class FinanceModels(function_params.FunctionParams):
    model: FinanceModelInput = pydantic.Field(description="Load a financial model")
    _input_names = pydantic.PrivateAttr(default=["in"])
    _output_names = pydantic.PrivateAttr(default=["out"])

    def get_metadata(self) -> FinanceModelMetadata:
        return FinanceModelMetadata(
            num_model_qubits=self.model.params.num_model_qubits,
            distribution_range=self.model.params.distribution_range,
        )


class FinancePayoff(function_params.FunctionParams):
    finance_function: FinanceFunctionInput = pydantic.Field(
        description="The finance function to solve the model"
    )
    num_qubits: pydantic.PositiveInt
    distribution_range: Tuple[float, float]

    _input_names = pydantic.PrivateAttr(default=["in"])
    _output_names = pydantic.PrivateAttr(default=["out"])
