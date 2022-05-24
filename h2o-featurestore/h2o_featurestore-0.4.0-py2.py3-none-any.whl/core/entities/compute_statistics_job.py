from .base_job import BaseJob


class ComputeStatisticsJob(BaseJob):
    def _response_method(self, job_id):
        self._stub.GetComputeStatisticsJobOutput(job_id)
