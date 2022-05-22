from typing import Any, Dict, List, Optional

from pyomo.core import ConcreteModel

from classiq.interface import status
from classiq.interface.backend.backend_preferences import BackendPreferences
from classiq.interface.chemistry import operator
from classiq.interface.combinatorial_optimization import (
    model_serializer,
    optimization_problem,
    sense,
)
from classiq.interface.combinatorial_optimization.encoding_types import EncodingType
from classiq.interface.combinatorial_optimization.preferences import QAOAPreferences
from classiq.interface.executor.optimizer_preferences import CombinatorialOptimizer
from classiq.interface.executor.result import ExecutionData, ExecutionStatus
from classiq.interface.generator import result as generator_result
from classiq.interface.generator.result import GeneratedCircuit

from classiq._internals.api_wrapper import ApiWrapper
from classiq._internals.async_utils import Asyncify
from classiq._internals.type_validation import validate_type
from classiq.exceptions import (
    ClassiqError,
    ClassiqExecutionError,
    ClassiqGenerationError,
)


class CombinatorialOptimization(metaclass=Asyncify):
    def __init__(
        self,
        model: ConcreteModel,
        qaoa_preferences: Optional[QAOAPreferences] = None,
        optimizer_preferences: Optional[CombinatorialOptimizer] = None,
        backend_preferences: Optional[BackendPreferences] = None,
        encoding_type: Optional[EncodingType] = None,
    ):
        self.is_maximization = sense.is_maximization(model)
        self._serialized_model = model_serializer.to_json(model, return_dict=True)

        arguments: Dict[str, Any] = {
            "serialized_model": self._serialized_model,
            "encoding_type": encoding_type,
        }
        if qaoa_preferences is not None:
            arguments["qaoa_preferences"] = qaoa_preferences
        if optimizer_preferences is not None:
            arguments["optimizer_preferences"] = optimizer_preferences
        if backend_preferences is not None:
            arguments["backend_preferences"] = backend_preferences

        self._problem = optimization_problem.OptimizationProblem(**arguments)

    async def generate_async(self) -> GeneratedCircuit:
        result = await ApiWrapper.call_combinatorial_optimization_generate_task(
            problem=self._problem
        )

        if result.status != generator_result.GenerationStatus.SUCCESS:
            raise ClassiqGenerationError(f"Solving failed: {result.details}")

        return validate_type(
            obj=result.details,
            expected_type=GeneratedCircuit,
            operation="Solving",
            exception_type=ClassiqGenerationError,
        )

    async def solve_async(self) -> ExecutionData:
        result = await ApiWrapper.call_combinatorial_optimization_solve_task(
            problem=self._problem
        )

        if result.status != ExecutionStatus.SUCCESS:
            raise ClassiqExecutionError(f"Solving failed: {result.details}")
        return result.details

    async def solve_classically_async(self) -> ExecutionData:
        result = (
            await ApiWrapper.call_combinatorial_optimization_solve_classically_task(
                problem=self._problem
            )
        )

        if result.status != ExecutionStatus.SUCCESS:
            raise ClassiqExecutionError(f"Solving failed: {result.details}")

        return result.details

    async def get_operator_async(self) -> operator.PauliOperator:
        result = await ApiWrapper.call_combinatorial_optimization_operator_task(
            problem=self._problem
        )

        if result.status != operator.OperatorStatus.SUCCESS:
            raise ClassiqError(f"Get operator failed: {result.details}")
        return validate_type(
            obj=result.details,
            expected_type=operator.PauliOperator,
            operation="Get operator",
            exception_type=ClassiqGenerationError,
        )

    async def get_objective_async(self) -> str:
        result = await ApiWrapper.call_combinatorial_optimization_objective_task(
            problem=self._problem
        )

        if result.status != status.Status.SUCCESS:
            raise ClassiqError(f"Get objective failed: {result.details}")

        return result.details

    async def get_initial_point_async(self) -> List[float]:
        result = await ApiWrapper.call_combinatorial_optimization_initial_point_task(
            problem=self._problem
        )

        if result.status != status.Status.SUCCESS:
            raise ClassiqError(f"Get inital point failed: {result.details}")

        return result.details
