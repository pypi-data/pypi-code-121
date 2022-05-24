import featurestore.core.CoreService_pb2 as pb

from . import interactive_console
from .config import ConfigUtils
from .utils import Utils


class JobInfo:
    def __init__(self, stub, job_id):
        self._stub = stub
        self._job_id = job_id
        self._next_index = 0

    def show_progress(self):
        if ConfigUtils.is_interactive_print_enabled():
            request = pb.JobProgressInput(
                job_id=self._job_id.job_id, next_index=self._next_index
            )
            response = self._stub.GetJobProgress(request)
            if response.progress:
                self._next_index += len(response.progress)
                for progress in response.progress:
                    interactive_console.log(
                        f"Job ID: {self._job_id.job_id}, Status: {progress.message}"
                    )

    def get_metrics(self):
        if self._stub.GetJob(self._job_id).done:
            request = pb.JobProgressInput(job_id=self._job_id.job_id, next_index=0)
            response = self._stub.GetJobProgress(request)
            if response.progress:
                return {
                    progress.message: f"{progress.duration_in_seconds}s"
                    for progress in response.progress
                }
        else:
            interactive_console.log(
                "Job is still running. Please wait until the job finishes."
            )
