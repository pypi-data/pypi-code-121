import ast
import enum
import keyword
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

import pydantic

from classiq.interface.generator.arith.fix_point_number import (
    MAX_FRACTION_PLACES,
    FixPointNumber,
)
from classiq.interface.generator.arith.register_user_input import RegisterUserInput
from classiq.interface.generator.function_params import FunctionParams
from classiq.interface.helpers.custom_pydantic_types import pydanticExpressionStr

DEFAULT_ARG_NAME = "in_arg"
DEFAULT_TARGET_NAME = "arithmetic_target"

SUPPORTED_FUNC_NAMES = ("CLShift", "CRShift", "min", "max")
SUPPORTED_VAR_NAMES_REG = "[A-Za-z][A-Za-z0-9]*"

white_list = {"or", "and"}.union(SUPPORTED_FUNC_NAMES)
black_list = set(keyword.kwlist) - white_list


class UncomputationMethods(str, enum.Enum):
    naive = "naive"
    optimized = "optimized"


class MappingMethods(str, enum.Enum):
    naive = UncomputationMethods.naive.value
    optimized = UncomputationMethods.optimized.value
    no_uncomputation = "none"


SingleArithmeticDefinition = Union[
    pydantic.StrictInt, pydantic.StrictFloat, FixPointNumber, RegisterUserInput
]
ArithmeticDefinitions = Dict[str, SingleArithmeticDefinition]


class ArithmeticTemplate(FunctionParams, ABC):
    max_fraction_places: pydantic.NonNegativeInt = MAX_FRACTION_PLACES
    expression: pydanticExpressionStr
    definitions: ArithmeticDefinitions
    qubit_count: Optional[pydantic.NonNegativeInt] = None

    @pydantic.validator("expression")
    def check_expression_is_legal(cls, expression):
        try:
            ast.parse(expression, "", "eval")
        except SyntaxError:
            raise ValueError(f"Failed to parse expression '{expression}'")
        return expression

    @pydantic.root_validator()
    def check_all_variable_are_defined(cls, values):
        expression, definitions = values.get("expression"), values.get("definitions")

        literals = set(re.findall(SUPPORTED_VAR_NAMES_REG, expression))

        not_allowed = literals.intersection(black_list)
        undefined_literals = literals.difference(definitions, white_list)
        if not_allowed:
            raise ValueError(f"The following names: {not_allowed} are not allowed")

        if undefined_literals:
            raise ValueError(f"{undefined_literals} need to be defined in definitions")
        return values

    @pydantic.root_validator()
    def substitute_expression(cls, values):
        # TODO there isn't a secure way to simplify the expression which does not involve using eval.
        #  Can be done with sdk on client side
        try:
            expression = values["expression"]
            definitions = values["definitions"]
        except KeyError:
            raise ValueError("Valid expression and definition are required")
        new_definition = dict()
        for var_name, value in definitions.items():
            if isinstance(value, RegisterUserInput):
                new_definition[var_name] = value
                continue
            elif isinstance(value, int):
                pass
            elif isinstance(value, float):
                value = FixPointNumber(float_value=value).actual_float_value
            elif isinstance(value, FixPointNumber):
                value = value.actual_float_value
            else:
                raise ValueError(f"{type(value)} type is illegal")

            expression = re.sub(r"\b" + var_name + r"\b", str(value), expression)
        values["expression"] = expression
        values["definitions"] = new_definition
        return values

    @pydantic.validator("definitions")
    def set_register_names(cls, definitions):
        for k, v in definitions.items():
            if isinstance(v, RegisterUserInput):
                v.name = k
        return definitions

    def _create_io_names(self):
        literals = set(re.findall("[A-Za-z][A-Za-z0-9]*", self.expression))
        self._input_names = [
            literal for literal in literals if literal not in white_list
        ] + self._target_input_names
        self._output_names = self._result_output_names

    @property
    @abstractmethod
    def _target_input_names(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def _result_output_names(self) -> List[str]:
        pass

    class Config:
        extra = "forbid"


class Arithmetic(ArithmeticTemplate):
    output_name: str = "expression_result"
    target: Optional[RegisterUserInput] = None
    uncomputation_method: MappingMethods = MappingMethods.optimized
    allow_input_override: bool = True

    @pydantic.validator("target", always=True)
    def _validate_target_name(
        cls, target: Optional[RegisterUserInput], values: Dict[str, Any]
    ) -> Optional[RegisterUserInput]:
        if target is None:
            return None

        if target.name is None:
            target.name = DEFAULT_TARGET_NAME

        if target.name == values.get("output_name"):
            raise ValueError("Target and output wires cannot have the same name")

        return target

    @property
    def _target_input_names(self) -> List[str]:
        if self.target and self.target.name:
            return [self.target.name]
        return list()

    @property
    def _result_output_names(self) -> List[str]:
        return [self.output_name]


class ArithmeticOracle(ArithmeticTemplate):
    uncomputation_method: UncomputationMethods = UncomputationMethods.optimized

    @pydantic.validator("expression")
    def validate_compare_expression(cls, value):
        ast_obj = ast.parse(value, "", "eval")
        if not isinstance(ast_obj, ast.Expression):
            raise ValueError("Must be an expression")
        if not isinstance(ast_obj.body, (ast.Compare, ast.BoolOp)):
            raise ValueError("Must be a comparison expression")

        return value

    @property
    def _target_input_names(self) -> List[str]:
        return list()

    @property
    def _result_output_names(self) -> List[str]:
        return list()

    @staticmethod
    def _arithmetic_expression_output_name() -> str:
        return "expression_result"

    def get_arithmetic_expression_params(self) -> Arithmetic:
        return Arithmetic(
            max_fraction_places=self.max_fraction_places,
            expression=self.expression,
            definitions=self.definitions,
            uncomputation_method=self.uncomputation_method,
            qubit_count=self.qubit_count,
            output_name=self._arithmetic_expression_output_name(),
            target=RegisterUserInput(size=1),
            allow_input_override=False,
        )
