from strangeworks.errors.error import StrangeworksError
import time
from typing import Any, Callable, Dict, List, Optional, Type
from datetime import datetime
from qiskit.providers.ibmq.runtime import RuntimeProgram, ParameterNamespace
from qiskit.providers.ibmq.runtime.program.result_decoder import ResultDecoder
from qiskit.providers.jobstatus import JobStatus, JOB_FINAL_STATES
from qiskit.providers.exceptions import JobTimeoutError
from qiskit.providers.ibmq.runtime.exceptions import (
    RuntimeInvalidStateError,
    RuntimeJobFailureError,
)
from logging import getLogger


class RuntimeJob:
    def __init__(
        self,
        api_client,
        job_id: str,
        result_id: str,
        result_data_id: str,
        program_id: str,
        results: str,
        backend: str = "",
        status: JobStatus = JobStatus.INITIALIZING,
        inputs: Optional[Dict] = None,
        params: Optional[Dict] = None,
        creation_date: Optional[str] = None,
        user_callback: Optional[Callable] = None,
        result_decoder: Type[ResultDecoder] = ResultDecoder,
        interim_results: List = None,
        polling_wait: int = 5,
    ) -> None:
        self._job_id = job_id
        self.result_id = result_id
        self.result_data_id = result_data_id
        self._interim_results = interim_results
        self._results = results
        self._inputs = inputs or {}
        self._params = params or {}
        self._creation_date = creation_date
        self._program_id = program_id
        self._status = status
        self._backend = backend
        self.__runtime_client = api_client
        self.__result_decoder = result_decoder or ResultDecoder
        self.__polling_wait = polling_wait
        self._user_callback = user_callback

    def result(
        self,
        timeout: Optional[float] = None,
        wait: float = 5,
        decoder: Optional[Type[ResultDecoder]] = None,
    ) -> Any:
        __decoder = decoder or self.__result_decoder
        if not self._results or (__decoder != self.__result_decoder):
            self.__wait_for_final_state(timeout=timeout, wait=wait)
            results = self.__runtime_client.fetch_job(job_id=self._job_id)
            if self._status == JobStatus.ERROR:
                raise RuntimeJobFailureError(
                    f"Unable to retrieve result for job {self._job_id}."
                    f"Job has failed:\n{results._results}"
                )
            self._results = __decoder.decode(results._results)
            self._interim_results = results._interim_results
            # once interim results are fetched return none
            if len(self._interim_results) and self._user_callback is not None:
                self._user_callback(self._job_id, self._interim_results)
                self._user_callback = None
        return self._results

    def cancel(self) -> None:
        """Cancel the job"""
        result = self.__runtime_client.cancel_job(self._job_id)
        if result.status_code != 204:
            raise Exception(result.json)
        return

    def get_status(self) -> JobStatus:
        """Fetch the status of the job"""
        job = self.__runtime_client.fetch_job(self._job_id)
        self._status = job._status
        if self._status == "cancelled":
            raise StrangeworksError.new_error(
                message="The runtime job was cancelled ", exception=None
            )
        if job._results is not None and job._results != "":
            self._results = job._results
        return self._status

    def __retry_get_status(self, retry_count=0) -> JobStatus:
        if retry_count > 10:
            raise Exception("retry limit reached attempting to fetch job")
        try:
            return self.get_status()
        except Exception as e:
            l = getLogger()
            l.error(f"exception trying to fetch status {e}")
            retry_count += 1
            time.sleep(self.__polling_wait)
            return self.__retry_get_status(retry_count)

    def __wait_for_final_state(self, timeout: Optional[float], wait: float) -> None:
        start_time = time.time()
        status = self.__retry_get_status(0)
        while status not in JOB_FINAL_STATES:
            elapsed_time = time.time() - start_time
            if timeout is not None and elapsed_time >= timeout:
                raise JobTimeoutError(
                    "Timeout while waiting for job {}.".format(self.job_id())
                )
            status = self.__retry_get_status(0)
            time.sleep(wait)

    def stream_results(
        self, callback: Callable, decoder: Optional[Type[ResultDecoder]] = None
    ) -> None:
        """Start streaming job results. Matches IBM signature, but utilizes polling vs websockets

        Args:
            callback: Callback function to be invoked for any interim results.
                The callback function will receive 2 positional parameters:
                    1. Job ID
                    2. Job interim result.
            decoder: A :class:`ResultDecoder` subclass used to decode job results.
        Raises:
            RuntimeInvalidStateError: If a callback function is already streaming results or
                if the job already finished.
        """
        if self._status in JOB_FINAL_STATES:
            raise RuntimeInvalidStateError("Job already finished.")
        if self.__is_streaming:
            raise RuntimeInvalidStateError("already streaming")
        raise RuntimeInvalidStateError(
            "Result streaming not currently implemented, but interim results are returned when calling for results. Callback function will be called once when interim results are fetched"
        )

    def cancel_result_streaming(self) -> None:
        self.__is_streaming = False

    def job_id(self) -> str:
        """Return a unique ID identifying the job.
        Returns:
            Job ID.
        """
        return self._job_id

    def backend(self) -> str:
        """Return the backend where this job was executed.
        Returns:
            Backend used for the job.
        TODO: Return Backend object
        """
        return self._backend

    @property
    def inputs(self) -> Dict:
        """Job input parameters.
        Returns:
            Input parameters used in this job.
        """
        return self._params

    @property
    def program_id(self) -> str:
        """Program ID.
        Returns:
            ID of the program this job is for.
        """
        return self._program_id

    @property
    def creation_date(self) -> Optional[datetime]:
        """Job creation date in local time.
        Returns:
            The job creation date as a datetime object, in local time, or
            ``None`` if creation date is not available.
        """
        return self._creation_date


class StrangeworksRuntimeService:
    def __init__(self, provider, runtime_client) -> None:
        self.__runtime_client = runtime_client
        self.__provider = provider
        return

    def pprint_programs(self, refresh: bool = False) -> None:
        """Pretty print programs"""
        programs = self.__runtime_client.fetch_programs()
        for prog in programs:
            print("=" * 50)
            print(str(prog))
        return

    def programs(self, refresh: bool = False) -> List[RuntimeProgram]:
        """Return available runtime programs"""
        return self.__runtime_client.fetch_programs()

    def program(self, program_id: str, refresh: bool = False) -> RuntimeProgram:
        """return a runtime program"""
        return self.__runtime_client.fetch_program(program_id)

    def run(
        self,
        program_id: str = "",
        strangeworks_result_id: str = None,
        options: Dict = {},
        inputs: Dict = {},
        callback: Optional[Callable] = None,
        result_decoder: Optional[Type[ResultDecoder]] = None,
    ) -> RuntimeJob:
        """
        Run a runtime job via the Strangeworks API
        """

        # must include a backend
        backend_name = options.get("backend_name", "")
        if backend_name == "":
            raise Exception("must include backend_name in options")

        # If using params object, extract as dictionary
        if isinstance(inputs, ParameterNamespace):
            inputs.validate()
            inputs = vars(inputs)

        return self.__runtime_client.run_job(
            program_id=program_id,
            backend=backend_name,
            params=inputs,
            strangeworks_result_id=strangeworks_result_id,
            callback=callback,
            result_decoder=result_decoder,
        )

    def upload_program(self) -> str:
        raise Exception("not available")

    def delete_program(self, program_id: str) -> None:
        raise Exception("not available")

    def job(self, job_id: str) -> RuntimeJob:
        return self.__runtime_client.fetch_job(job_id)

    def delete_job(self, job_id: str) -> None:
        self.__runtime_client.cancel_job(job_id)
        return
