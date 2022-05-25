from copy import copy, deepcopy
from time import sleep
from typing import List, Union, Callable
from uuid import UUID

from bodosdk.api.auth import AuthApi
from bodosdk.api.job import JobApi
from bodosdk.exc import ResourceNotFound, Unauthorized, WaiterTimeout
from bodosdk.models import JobStatus
from bodosdk.models.job import JobDefinition, JobResponse, JobExecution


class JobWaiter:

    def __init__(self, client):
        """
        Object for waiting till job finishes

        :param client:
        :type client: JobClient
        """
        self._client = client

    def wait(self, uuid, on_success: Callable = None, on_failure: Callable = None, on_timeout: Callable = None,
             check_period=10, timeout=None):
        """
        Method to wait for specific job to finished, returns job object or results of callbacks if defined

        :param uuid: job uuid
        :param on_success: callback to be called on success, job object is passed into
        :param on_failure: callback to be called on failure, job object is passed into
        :param on_timeout: callback to be called on failure, job uuid passed into. If no callback WaiterTimeout exception raised
        :param check_period: how often waiter should check
        :param timeout: how long waiter should try, None means infinity
        :return: job response or result of callbacks
        :raises WaiterTimeout: when timeout and no on_timeout callback defined
        """
        job: JobResponse = self._client.get(uuid)
        while job.status not in (JobStatus.FINISHED, JobStatus.FAILED):
            sleep(check_period)
            timeout = timeout - check_period if timeout else timeout
            if timeout is not None and timeout <= 0:
                if on_timeout:
                    return on_timeout(uuid)
                raise WaiterTimeout
            job: JobResponse = self._client.get(uuid)
        if job.status == JobStatus.FINISHED and on_success:
            return on_success(job)
        if job.status == JobStatus.FAILED and on_failure:
            return on_failure(job)
        return job


class JobClient:
    def __init__(self, api: JobApi):
        self._api = api

    def create(self, job_definition: JobDefinition) -> JobResponse:
        """
        Creates a job and job dedicated cluster

        :param job_definition:
            definition of job and cluster
        :type job_definition: JobDefinition
        :return: created job data
        :rtype: JobDefinition
        :raises Unauthorized: when keys are invalid
        :raises ValidationError: when JobDefinition is invalid
        """
        try:
            return self._api.create_job(job_definition)
        except ResourceNotFound:
            raise Unauthorized

    def remove(self, job_uuid: Union[str, UUID]) -> None:
        """
        Removes job and it's cluster

        :param job_uuid:
        :type job_uuid: Union[str, UUID]
        :return: None
        :rtype: None
        :raises ResourceNotFound:
        """
        self._api.delete_job(str(job_uuid))

    def list(self) -> List[JobResponse]:
        """
        List all jobs in workspace

        :return: list of jobs
        :rtype: List[JobResponse]
        """
        return self._api.list_jobs()

    def get(self, uuid: Union[str, UUID]) -> JobResponse:
        """
        Gets specific job from workspace

        :param uuid:
        :type uuid: Union[str, UUID]
        :return: job data
        :rtype: JobResponse
        :raises ResourceNotFound:
        """
        return self._api.get_job(str(uuid))

    def get_job_executions(self, uuid: Union[str, UUID]) -> List[JobExecution]:
        """
        Returns job executions for specific job

        :param uuid:
        :type uuid: Union[str, UUID]
        :return: list of job executions
        :rtype: List[JobExecution]
        :raises ResourceNotFound:
        """
        return self._api.get_tasks(str(uuid))

    def get_waiter(self) -> JobWaiter:
        """
        Returns waiter
        :return: a helper waiting till job finishes
        :rtype: JobWaiter
        """
        return JobWaiter(
            client=deepcopy(self)
        )
