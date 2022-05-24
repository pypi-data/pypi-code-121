from .base_job import BaseJob


class RevertIngestJob(BaseJob):
    def _response_method(self, job_id):
        self._stub.GetRevertIngestJobOutput(job_id)
