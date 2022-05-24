from ..utils import Utils
from .base_job import BaseJob


class MaterializationOnlineJob(BaseJob):
    def _response_method(self, job_id):
        response = self._stub.GetMaterializationOnlineJobOutput(job_id)
        return MaterializationOnlineResponse(response)


class MaterializationOnlineResponse:
    def __init__(self, response):
        self._response = response
        self._materialization_scope = response.materialization_scope
        self._num_records = response.num_records

    def get_materialization_scope(self):
        return self._materialization_scope

    def get_num_records(self):
        return self._num_records

    def __repr__(self):
        return Utils.pretty_print_proto(self._response)
