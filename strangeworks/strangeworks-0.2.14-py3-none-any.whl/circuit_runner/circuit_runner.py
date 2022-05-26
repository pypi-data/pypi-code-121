from strangeworks.backend.backends import Backend, BackendService
from strangeworks.jobs.jobs import Job
from strangeworks.errors.error import StrangeworksError
from strangeworks.rest_client.rest_client import StrangeworksRestClient
from typing import Union, List
import uuid


class CircuitRunner:
    def __init__(
        self,
        rest_client: StrangeworksRestClient,
        result_id: str = None,
        backend: str = None,
        backends: list = [],
    ) -> None:
        self.__rest_client = rest_client
        if self.__rest_client is None:
            raise StrangeworksError.invalid_argument(
                message="must include rest_client when initializing CircuitRunner class, try using the default CircuitRunner client: strangeworks.circuit_runner...",
            )
        self.__result_id = result_id
        self.__backend_service = BackendService(rest_client, backend, backends)

    def _new_client(self, rest_client: StrangeworksRestClient = None):
        self.__rest_client = rest_client
        self.__backend_service = BackendService(rest_client)

    def get_backends(
        self, selected_backend: Union[str, Backend] = None, pprint: bool = True
    ) -> List[Backend]:
        return self.__backend_service.get_backends(
            selected_backend,
            pprint,
            filters=lambda b: b.backend_type() == "gate_model",
        )

    def select_backend(self, selected_backend: Union[str, Backend] = None) -> Backend:
        return self.__backend_service.select_backend(selected_backend)

    def run(
        self,
        payload: dict,
        shots: int = 1,
        backend: Union[str, Backend] = None,
        async_execution: bool = False,
        *args,
        **kwargs,
    ):
        if backend:
            self.__backend_service.select_backend(backend)

        # create a new result for each job unless the user specifies a result in the client
        result_id = (
            self.__result_id if self.__result_id is not None else str(uuid.uuid4())
        )
        b = self.__backend_service.selected_backend()
        if b.backend_type() != "gate_model":
            raise StrangeworksError.invalid_argument(
                f"{b.name()} is not a supported backend for circuit runner"
            )

        if "circuit" not in payload or "circuit_type" not in payload:
            raise StrangeworksError.invalid_argument(
                "Utilize one of the strangeworks extensions to convert your input"
            )
        circuit_runner_payload = {
            "target": b.name(),
            "shots": shots,
            "result_id": result_id,
        }

        circuit_runner_payload.update(kwargs)
        circuit_runner_payload.update(payload)

        response = self.__rest_client.post(
            url=f"{b.plugin_url()}/run-job",
            json=circuit_runner_payload,
            expected_response=200,
        )

        # if job is async return the raw results
        if async_execution:
            return response

        return Job.from_json(
            job=response,
            backend=self.__backend_service.selected_backend(),
            rest_client=self.__rest_client,
        )
