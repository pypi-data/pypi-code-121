from ..utils import Utils
from .base_job import BaseJob


class IngestJob(BaseJob):
    def _response_method(self, job_id):
        response = self._stub.GetIngestJobOutput(job_id)
        return IngestResponse(response)


class IngestResponse:
    def __init__(self, response):
        self._response = response
        self._meta = response.meta

    def _get_feature_set(self):
        return self._response.feature_set

    def __repr__(self):
        return Utils.pretty_print_proto(self._meta)
