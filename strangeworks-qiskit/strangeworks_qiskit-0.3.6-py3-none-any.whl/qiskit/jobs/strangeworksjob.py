import strangeworks

import time, json

from abc import ABC

from qiskit.providers import JobV1 as Job, JobStatus
from qiskit.providers.exceptions import JobTimeoutError
from qiskit.providers import JobError
from qiskit.providers.jobstatus import JOB_FINAL_STATES
from qiskit.result import Result

from strangeworks.qiskit._hw_api import SWClient
from strangeworks.errors.error import StrangeworksError


class StrangeworksJob(Job):
    def __init__(self, backend, job_id: str, circuit, remote, **kwargs) -> None:
        if remote:
            self._job = _SWRemoteJob(backend, job_id, circuit, **kwargs)
        else:
            self._job = _SWLocalJob(backend, job_id, circuit, **kwargs)

    def job_id(self):
        return self._job.job_id()

    def backend(self):
        return self._job.backend()

    def done(self):
        return self._job.done()

    def running(self):
        return self._job.running()

    def cancelled(self):
        return self._job.cancelled()

    def in_final_state(self):
        return self._job.in_final_state()

    def wait_for_final_state(self, timeout=None, wait=5, callback=None):
        self._job.wait_for_final_state(timeout, wait, callback)

    def submit(self):
        self._job.submit()

    def result(self):
        return self._job.result()

    def cancel(self):
        self._job.cancel()

    def status(self):
        return self._job.status()

    @classmethod
    def get(cls, job_id: str) -> "StrangeworksJob":
        job = cls(None, job_id, None, True)
        job._job = _SWRemoteJob.get_job(job_id)
        return job

    def strangeworks_result_url(self) -> str:
        return self._job.strangeworks_result_url()


# all these calsses should not be exported ;)
class _SWJob(Job, ABC):
    def __init__(self, backend, job_id: str, circuit, **kwargs) -> None:
        super().__init__(backend, job_id, **kwargs)
        self._job_id = job_id
        self._circuit = circuit
        self._run_config = kwargs
        self._result = None
        self._status = JobStatus.INITIALIZING

    def job_id(self):
        return self._job_id

    def result(self):
        if self._result is not None:
            return self._result
        try:
            self.wait_for_final_state()
        except JobTimeoutError as ex:
            raise Exception("Timed out waiting for job to complete") from ex
        return self._result


class _SWLocalJob(_SWJob):
    def __init__(self, backend, job_id: str, circuit, **kwargs) -> None:
        super().__init__(backend, job_id, circuit, **kwargs)
        self._client = strangeworks.client

    def submit(self):
        parameters = None
        if not self._circuit:
            raise Exception(
                "You must submit a circuit when running a job on your local backend."
            )

        # blocking simulation and format results
        backend = self.backend()
        simulator = getattr(backend, "simulator", None)
        if not simulator:
            self._status = JobStatus.ERROR
            return

        job = simulator.run(self._circuit, **self._run_config)
        self._result = job.result()
        self._status = JobStatus.ERROR
        if self._result:
            self._status = JobStatus.DONE
            self._job_id = job.job_id()

    def status(self):
        return self._status

    def cancel(self):
        pass


class _SWRemoteJob(_SWJob):
    def __init__(self, backend, job_id: str, circuit, **kwargs) -> None:
        super().__init__(backend, job_id, circuit, **kwargs)
        self._client = SWClient(strangeworks.client)
        if backend and backend._client:
            self._client = backend._client
        self._result_url = ""

    def submit(self):
        job = self._client.create_job(
            self._circuit, self.backend().name(), **self.metadata
        )
        self._job_id = job["id"]
        if "status" in job:
            self._status = JobStatus(job["status"])
        if "result" in job:
            self._result = Result.from_dict(job["result"]["data"])

    def status(self):
        if self._job_id is None:
            return self._status

        response = self._client.fetch_job_status(self._job_id)

        status = response["status"]
        self._status = JobStatus(status)

        if self._status in JOB_FINAL_STATES:
            if not self._result:
                self._result = self._get_result(response)

        return self._status

    def cancel(self):
        self._client.cancel_job(self._job_id)

    # assumes your Job.Status is in a JOB_FINAL_STATE
    def _get_result(self, response):
        if self._status == JobStatus.CANCELLED:
            raise StrangeworksError(
                f"Unable to get a result from a cancelled job {self.job_id()}"
            )

        wait = 5
        result = None
        while "result" not in response or not result:
            response = self._client.fetch_job_status(self._job_id)
            if "result" in response:
                result = response["result"]
                if result and "data" in result:
                    break
                result = None
            time.sleep(wait)

        if "job_zip_url" in response:
            self._result_url = response["job_zip_url"]

        data = result["data"]

        if self._status == JobStatus.ERROR:
            raise StrangeworksError(
                f"Unable to get a result from an errored job {self.job_id()}\n{data}"
            )

        if isinstance(data, dict):
            return Result.from_dict(data)

        res = json.loads(data)
        return Result.from_dict(res)

    @classmethod
    def get_job(cls, job_id: str) -> "_SWRemoteJob":
        j = _SWRemoteJob(None, job_id, None)
        response = j._client.fetch_job(job_id)
        j._job_id = response["id"]
        j._status = JobStatus(response["status"])
        if j._status in JOB_FINAL_STATES:
            j._result = j._get_result(response)
        # todo: figure out if we need the backend & circuit
        return j

    def strangeworks_result_url(self) -> str:
        return self._result_url
