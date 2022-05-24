import json

from .. import CoreService_pb2 as pb
from ..retrieve_holder import RetrieveAsLinksCommon
from .base_job import BaseJob


class RetrieveJob(BaseJob, RetrieveAsLinksCommon):
    def _response_method(self, job_id):
        response = self._stub.GetRetrieveAsLinksJobOutput(job_id)
        return response.download_links

    def __repr__(self):
        return json.dumps(
            {
                "job_id": self._job.job_id,
                "job_type": pb.JobType.Name(self._job.job_type),
                "job_done": bool(self._job.done),
                "child_job_ids": self._job.childJobIds,
            }
        )
