import functools
import json
import logging
from typing import Dict, Optional, Type, TypeVar

import httpx
import pydantic
import websockets.client
import websockets.exceptions
import websockets.typing
from typing_extensions import Protocol

from classiq.interface.analyzer import analysis_params, result as analysis_result
from classiq.interface.analyzer.analysis_params import AnalysisRBParams
from classiq.interface.applications.qsvm import (
    QSVMData,
    QSVMPredictResult,
    QSVMResult,
    QSVMResultStatus,
    QSVMTestResult,
    QSVMTrainResult,
)
from classiq.interface.chemistry import (
    ground_state_problem,
    ground_state_solver,
    operator,
)
from classiq.interface.combinatorial_optimization import (
    optimization_problem,
    result as opt_result,
)
from classiq.interface.executor import execution_request, result as execute_result
from classiq.interface.generator import result as generator_result
from classiq.interface.generator.model import Model
from classiq.interface.jobs import AUTH_HEADER, JobDescription, JobStatus, JSONObject
from classiq.interface.server import routes

from classiq._internals.client import client
from classiq._internals.jobs import JobPoller
from classiq.exceptions import ClassiqQSVMError, ClassiqValueError

_FAIL_FAST_INDICATOR = "{"
ResultType = TypeVar("ResultType", bound=pydantic.BaseModel)


class StatusType(Protocol):
    ERROR: str


def _retry_websocket_on_exception(func):
    # TODO fix this workaround
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except websockets.exceptions.InvalidStatusCode as exc:
            # If the token is missing or invalid, the handshake fails
            # with a status code of 403. In this case, we refresh the token
            # and try again.
            if exc.status_code == httpx.codes.FORBIDDEN.value:
                await client().update_expired_access_token()
                return await func(*args, **kwargs)
            raise

    return wrapped


def _decode_message(msg: websockets.typing.Data) -> str:
    return msg.decode() if isinstance(msg, bytes) else msg


async def _get_return_value_from_websocket(
    websocket: websockets.client.WebSocketClientProtocol,
) -> str:
    is_first = True
    msg: str = _decode_message(await websocket.recv())

    while msg:
        logging.info(msg)

        # HACK: This is meant to handle validation errors. It is a duplicate
        # of a similar hack implemented in the VS code extension
        if is_first:
            is_first = False
            if msg.startswith(_FAIL_FAST_INDICATOR):
                return msg

        msg = _decode_message(await websocket.recv())

    return _decode_message(await websocket.recv())


def _unpack_results(
    result: JobDescription[JSONObject],
    status_type: Type[StatusType],
    result_type: Type[ResultType],
) -> ResultType:
    description = result.description
    if result.status != JobStatus.COMPLETED:
        return result_type(
            status=description.get("status", status_type.ERROR),
            details=description["details"],
        )
    return result_type.parse_obj(result.description)


class ApiWrapper:
    _AUTH_HEADERS = {AUTH_HEADER}

    @classmethod
    async def _call_task(cls, http_method: str, url: str, body: Optional[Dict] = None):
        res = await client().call_api(http_method=http_method, url=url, body=body)
        if not isinstance(res, dict):
            raise ClassiqValueError(f"Unexpected returned value: {res}")
        return res

    @classmethod
    async def call_generation_task(
        cls, model: Model
    ) -> generator_result.GenerationResult:
        poller = JobPoller(base_url=routes.TASKS_GENERATE_FULL_PATH)
        # TODO Support smarter json serialization
        model_dict = json.loads(model.json())
        result = await poller.run(body=model_dict, timeout_sec=None)
        return _unpack_results(
            result,
            status_type=generator_result.GenerationStatus,
            result_type=generator_result.GenerationResult,
        )

    @staticmethod
    def _is_async_execute_task(request: execution_request.ExecutionRequest):
        return (
            isinstance(
                request.execution_payload, execution_request.QuantumProgramExecution
            )
            and request.execution_payload.syntax
            == execution_request.QuantumInstructionSet.IONQ
        )

    @classmethod
    async def _call_blocking_execute_task(
        cls, request: Dict
    ) -> execute_result.ExecutionResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.EXECUTE_TASKS_FULL_PATH,
            body=request,
        )
        return execute_result.ExecutionResult.parse_obj(data)

    @classmethod
    async def _call_async_execute_task(
        cls, request: Dict
    ) -> execute_result.ExecutionResult:
        poller = JobPoller(
            base_url=routes.EXECUTE_ASYNC_TASKS_FULL_PATH,
            required_headers=cls._AUTH_HEADERS,
        )
        result = await poller.run(body=request, timeout_sec=None)
        return _unpack_results(
            result,
            status_type=execute_result.ExecutionStatus,
            result_type=execute_result.ExecutionResult,
        )

    @classmethod
    async def call_execute_task(
        cls, request: execution_request.ExecutionRequest
    ) -> execute_result.ExecutionResult:
        # TODO: request.dict() doesn't serialize complex class
        request_json = json.loads(request.json())
        if cls._is_async_execute_task(request):
            return await cls._call_async_execute_task(request_json)
        else:
            return await cls._call_blocking_execute_task(request_json)

    @classmethod
    async def call_analysis_task(
        cls, params: analysis_params.AnalysisParams
    ) -> analysis_result.AnalysisResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.ANALYZER_FULL_PATH,
            body=params.dict(),
        )

        return analysis_result.AnalysisResult.parse_obj(data)

    @classmethod
    async def call_analyzer_app(cls, analyzer_data: dict):
        data = await cls._call_task(
            http_method="post",
            url=routes.ANALYZER_UPLOAD_FULL_PATH,
            body=analyzer_data,
        )
        return analysis_result.AnalyzerFE.parse_obj(data)

    @classmethod
    async def call_rb_analysis_task(
        cls, params: AnalysisRBParams
    ) -> analysis_result.RbResults:
        data = await cls._call_task(
            http_method="post",
            url=routes.ANALYZER_RB_FULL_PATH,
            body=params.dict(),
        )

        return analysis_result.RbResults.parse_obj(data)

    @classmethod
    async def call_combinatorial_optimization_generate_task(
        cls, problem: optimization_problem.OptimizationProblem
    ) -> generator_result.GenerationResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_GENERATE_FULL_PATH,
            body=problem.dict(),
        )

        return generator_result.GenerationResult.parse_obj(data)

    @classmethod
    async def call_combinatorial_optimization_solve_task(
        cls,
        problem: optimization_problem.OptimizationProblem,
    ) -> execute_result.ExecutionResult:
        poller = JobPoller(
            base_url=routes.COMBINATORIAL_OPTIMIZATION_SOLVE_ASYNC_FULL_PATH
        )
        # TODO Support smarter json serialization
        problem_dict = json.loads(problem.json())
        result = await poller.run(body=problem_dict, timeout_sec=None)
        return _unpack_results(
            result,
            status_type=execute_result.ExecutionStatus,
            result_type=execute_result.ExecutionResult,
        )

    @classmethod
    async def call_combinatorial_optimization_solve_classically_task(
        cls, problem: optimization_problem.OptimizationProblem
    ) -> execute_result.ExecutionResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_SOLVE_CLASSICALLY_FULL_PATH,
            body=problem.dict(),
        )

        return execute_result.ExecutionResult.parse_obj(data)

    @classmethod
    async def call_combinatorial_optimization_operator_task(
        cls, problem: optimization_problem.OptimizationProblem
    ) -> operator.OperatorResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_OPERATOR_FULL_PATH,
            body=problem.dict(),
        )

        return operator.OperatorResult.parse_obj(data)

    @classmethod
    async def call_combinatorial_optimization_objective_task(
        cls, problem: optimization_problem.OptimizationProblem
    ) -> opt_result.PyomoObjectResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_OBJECTIVE_FULL_PATH,
            body=problem.dict(),
        )

        return opt_result.PyomoObjectResult.parse_obj(data)

    @classmethod
    async def call_combinatorial_optimization_initial_point_task(
        cls, problem: optimization_problem.OptimizationProblem
    ) -> opt_result.AnglesResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.COMBINATORIAL_OPTIMIZATION_INITIAL_POINT_FULL_PATH,
            body=problem.dict(),
        )

        return opt_result.AnglesResult.parse_obj(data)

    @classmethod
    async def call_qsvm_train(cls, qsvm_data: QSVMData) -> QSVMTrainResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.QSVM_TRAIN,
            body=qsvm_data.dict(),
        )

        result = QSVMResult.parse_obj(data)

        if result.status != QSVMResultStatus.SUCCESS:
            raise ClassiqQSVMError(f"Training failed: {result.details}")

        if not isinstance(result.result, QSVMTrainResult):
            raise ClassiqQSVMError("Invalid train result")

        return result.result

    @classmethod
    async def call_qsvm_test(cls, qsvm_data: QSVMData) -> QSVMTestResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.QSVM_TEST,
            body=qsvm_data.dict(),
        )

        result = QSVMResult.parse_obj(data)

        if result.status != QSVMResultStatus.SUCCESS:
            raise ClassiqQSVMError(f"Testing failed: {result.details}")

        if not isinstance(result.result, QSVMTestResult):
            raise ClassiqQSVMError("Invalid test result")

        return result.result

    @classmethod
    async def call_qsvm_predict(cls, qsvm_data: QSVMData) -> QSVMPredictResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.QSVM_PREDICT,
            body=qsvm_data.dict(),
        )

        result = QSVMResult.parse_obj(data)

        if result.status != QSVMResultStatus.SUCCESS:
            raise ClassiqQSVMError(f"Predicting failed: {result.details}")

        if not isinstance(result.result, QSVMPredictResult):
            raise ClassiqQSVMError("Invalid predict result")

        return result.result

    @classmethod
    async def call_generate_hamiltonian_task(
        cls, problem: ground_state_problem.GroundStateProblem
    ) -> operator.OperatorResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.CHEMISTRY_GENERATE_HAMILTONIAN_FULL_PATH,
            body=problem.dict(),
        )

        return operator.OperatorResult.parse_obj(data)

    @classmethod
    async def call_solve_exact_task(
        cls, problem: ground_state_problem.GroundStateProblem
    ) -> execute_result.ExecutionResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.CHEMISTRY_SOLVE_EXACT_FULL_PATH,
            body=problem.dict(),
        )

        return execute_result.ExecutionResult.parse_obj(data)

    @classmethod
    async def call_ground_state_solve_task(
        cls, problem: ground_state_solver.GroundStateSolver
    ) -> execute_result.ExecutionResult:
        data = await cls._call_task(
            http_method="post",
            url=routes.CHEMISTRY_SOLVE_FULL_PATH,
            body=problem.dict(),
        )

        return execute_result.ExecutionResult.parse_obj(data)
