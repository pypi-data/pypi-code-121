import json, uuid
from typing import Dict, List, Optional, Callable, Dict, Type

from strangeworks import Client
from qiskit.providers.ibmq.runtime import RuntimeProgram
from strangeworks.errors.error import StrangeworksError
from strangeworks.qiskit.backends._utils import get_provider_details
from .runtimes import RuntimeJob
from qiskit.providers.ibmq.runtime.constants import API_TO_JOB_STATUS
from qiskit.providers.ibmq.runtime.utils import RuntimeEncoder
from qiskit.providers.ibmq.runtime.program.result_decoder import ResultDecoder


class RuntimeClient:
    def __init__(self, client: Client):
        self.__base_url = f"/plugins/ibmq"
        self.__client = client

    def fetch_programs(self) -> List[RuntimeProgram]:
        """Fetch programs the user has access to"""
        response = self.__client.rest_client.get(f"{self.__base_url}/runtimes")
        runtime_programs = []
        for r in response:
            detail = r["ibmProgramDetail"]
            spec = detail["spec"]
            runtime_programs.append(
                RuntimeProgram(
                    program_name=detail["name"],
                    program_id=detail["id"],
                    description=detail["description"],
                    parameters=spec.get("parameters", None),
                    return_values=spec.get("return_values", None),
                    interim_results=spec.get("interim_results", None),
                    max_execution_time=detail["cost"],
                    backend_requirements=spec.get("backend_requirements", None),
                    creation_date=detail["creation_date"],
                    is_public=detail["is_public"],
                )
            )
        return runtime_programs

    def fetch_program(self, program_name) -> RuntimeProgram:
        """Fetch a single program"""
        response = self.__client.rest_client.get(
            f"{self.__base_url}/runtimes/{program_name}"
        )
        detail = response["ibmProgramDetail"]
        return RuntimeProgram(
            program_name=detail["ibm"]["name"],
            program_id=detail["id"],
            description=detail["description"],
            parameters=detail["parameters"],
            return_values=detail["return_values"],
            interim_results=detail["interim_results"],
            version=detail["version"],
            max_execution_time=detail["cost"],
            backend_requirements=detail["backend_requirements"],
        )

    def fetch_job(self, job_id) -> RuntimeJob:
        """Fetch a single job"""
        response = self.__client.rest_client.get(
            f"{self.__base_url}/runtimes/jobs/{job_id}"
        )
        return self.__json_to_runtime(response)

    def run_job(
        self,
        program_id: str,
        backend: str,
        params: dict,
        strangeworks_result_id: str = None,
        callback: Optional[Callable] = None,
        result_decoder: Optional[Type[ResultDecoder]] = None,
    ) -> RuntimeJob:
        """Run a program"""
        info = get_provider_details(backend)
        if not info:
            raise StrangeworksError(
                f"{backend} name is incorrect. Use StrangeworksProvider().backends() to find acceptable backends."
            )
        provider = info["provider"]
        if not provider or (provider == "" or provider != "ibm"):
            raise StrangeworksError(
                f"IBM runtimes does not support running on {backend}"
            )
        backend_name = info["backend_name"]
        hub, group, project = "", "", ""
        if "details" in info:
            hub = info["details"]["hub"]
            group = info["details"]["group"]
            project = info["details"]["project"]

        # use a new result_id for each new job run
        strangeworks_result_id = (
            str(uuid.uuid4())
            if strangeworks_result_id is None
            else strangeworks_result_id
        )

        response = self.__client.rest_client.post(
            f"{self.__base_url}/runtimes/jobs",
            json=self.__job_payload(
                program_id,
                hub,
                group,
                project,
                backend_name,
                params,
                strangeworks_result_id,
            ),
        )
        return self.__json_to_runtime(response, callback, result_decoder)

    def cancel_job(self, job_id) -> None:
        """cancel a running program"""
        self.__client.rest_client.delete(f"{self.__base_url}/runtimes/jobs/{job_id}")
        return

    def __job_payload(
        self,
        program_id: str,
        hub: str,
        group: str,
        project: str,
        backend: str,
        params: dict,
        strangeworks_result_id: str,
    ) -> object:
        return {
            "programId": program_id,
            "hub": hub,
            "group": group,
            "project": project,
            "backend": backend,
            "params": json.dumps(params, cls=RuntimeEncoder),
            "resultId": strangeworks_result_id,
        }

    def __json_to_runtime(
        self,
        json_response: Dict,
        callback: Optional[Callable] = None,
        result_decoder: Optional[Type[ResultDecoder]] = None,
    ) -> RuntimeJob:
        status = json_response.get("status", "")
        job_status = API_TO_JOB_STATUS.get(status.upper(), "")
        return RuntimeJob(
            api_client=self,
            job_id=json_response.get("id", ""),
            result_id=json_response.get("strangeworks_result_id", ""),
            result_data_id=json_response.get("strangeworks_result_data_id", ""),
            program_id=json_response.get("program_id", ""),
            results=json_response.get("results", ""),
            status=job_status,
            user_callback=callback,
            result_decoder=result_decoder,
            interim_results=json_response.get("interim_results", []),
        )
