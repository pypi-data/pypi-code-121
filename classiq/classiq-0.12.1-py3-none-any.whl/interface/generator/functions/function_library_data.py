from typing import Dict, Optional, Tuple, Type

import pydantic

from classiq.interface.generator.functions import function_data
from classiq.interface.generator.user_defined_function_params import CustomFunction
from classiq.interface.helpers.custom_pydantic_types import pydanticFunctionNameStr

DEFAULT_FUNCTION_LIBRARY_NAME = "default_function_library_name"


class FunctionLibraryData(pydantic.BaseModel):
    """Facility to store user-defined custom functions."""

    name: pydanticFunctionNameStr = pydantic.Field(
        default=DEFAULT_FUNCTION_LIBRARY_NAME,
        description="The name of the custom function library",
    )

    function_dict: Dict[str, function_data.FunctionData] = pydantic.Field(
        default_factory=dict,
        description="A dictionary containing the custom functions in the library.",
    )

    functions: Tuple[function_data.FunctionData, ...] = pydantic.Field(
        default=tuple(),
        description="A tuple for inputting custom functions to the library.",
    )

    @pydantic.validator("name")
    def validate_name(cls, name: str):
        function_data.validate_name_end_not_newline(name=name)
        return name

    @pydantic.validator("function_dict")
    def validate_function_dict(
        cls, function_dict: Dict[str, function_data.FunctionData]
    ):
        if not all(
            function_data.name == name for name, function_data in function_dict.items()
        ):
            raise AssertionError("Bad function_dict encountered.")
        return function_dict

    @pydantic.validator("functions")
    def validate_functions(
        cls, functions: Optional[Tuple[function_data.FunctionData, ...]], values
    ):
        if not functions:
            return None
        if values.get("function_dict"):
            raise ValueError("Expected only a single function data input field")
        values["function_dict"] = {
            function_data.name: function_data for function_data in functions
        }
        return None

    @staticmethod
    def validate_function_in_library(
        function_params: CustomFunction,
        library: Optional["FunctionLibraryData"],
        error_handler: Type[Exception] = ValueError,
    ) -> None:
        if library is None or function_params.name not in library.function_dict:
            raise error_handler("The function is not found in included library.")
