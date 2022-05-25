from typing import List

from bodosdk.api.base import BackendApi
from bodosdk.exc import ResourceNotFound, ServiceUnavailable, UnknownError, ValidationError
from bodosdk.models.job import JobDefinition, JobResponse, JobExecution, JobCreateResponse


class JobApi(BackendApi):

    def __init__(self, *args, **kwargs):
        super(JobApi, self).__init__(*args, **kwargs)
        self.resource_url = f"{self._base_url}/job"

    def create_job(self, job_definition: JobDefinition) -> JobResponse:
        headers = {
            'Content-type': 'application/json'
        }
        headers.update(self.get_auth_header())
        resp = self._requests.post(self._base_url + '/v2/job', data=job_definition.json(by_alias=True),
                                   headers=headers)
        if str(resp.status_code).startswith('2'):
            return JobCreateResponse(**resp.json())
        if resp.status_code == 404:
            raise ResourceNotFound("Probably wrong workspace keys")
        if resp.status_code in (400, 422):
            raise ValidationError(resp.json())
        if resp.status_code == 503:
            raise ServiceUnavailable
        raise UnknownError

    def delete_job(self, job_uuid) -> None:
        headers = self.get_auth_header()
        resp = self._requests.delete(f"{self.resource_url}/{job_uuid}", headers=headers)
        if resp.status_code == 200:
            return
        if resp.status_code == 404:
            raise ResourceNotFound
        if resp.status_code == 503:
            raise ServiceUnavailable
        raise UnknownError(resp.content)

    def list_jobs(self) -> List[JobResponse]:
        headers = self.get_auth_header()
        resp = self._requests.get(f"{self.resource_url}?withTasks=false", headers=headers)
        if resp.status_code == 503:
            raise ServiceUnavailable
        return [JobResponse(**data) for data in resp.json()]

    def get_job(self, uuid) -> JobResponse:
        headers = self.get_auth_header()
        resp = self._requests.get(f"{self.resource_url}/{uuid}", headers=headers)
        if resp.status_code == 404:
            raise ResourceNotFound
        if resp.status_code == 503:
            raise ServiceUnavailable
        return JobResponse(**resp.json())

    def get_tasks(self, uuid) -> List[JobExecution]:
        headers = self.get_auth_header()
        resp = self._requests.get(f"{self.resource_url}/{uuid}/tasks", headers=headers)
        if resp.status_code == 404:
            raise ResourceNotFound
        if resp.status_code == 503:
            raise ServiceUnavailable
        return [JobExecution(**data) for data in resp.json()]
