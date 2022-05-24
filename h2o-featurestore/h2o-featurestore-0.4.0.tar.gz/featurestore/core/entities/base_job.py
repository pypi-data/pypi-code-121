from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

from .. import CoreService_pb2 as pb
from ..job_info import JobInfo


class BaseJob(ABC):
    def __init__(self, stub, job_id):
        self._stub = stub
        self._job_id = job_id
        self._result = None
        self._job = self._stub.GetJob(self._job_id)
        self._thread_pool = ThreadPoolExecutor(5)
        self._info = JobInfo(self._stub, self._job_id)

    @property
    def id(self):
        return self._job_id.job_id

    @property
    def job_type(self):
        return pb.JobType.Name(self._job.job_type)

    @property
    def done(self):
        return self.is_done()

    @property
    def child_job_ids(self):
        return self._job.childJobIds

    @abstractmethod
    def _response_method(self, job_id):
        raise NotImplementedError(
            "Method `_response_method` needs to be implemented by the child class"
        )

    def is_done(self) -> bool:
        return self._stub.GetJob(self._job_id).done

    def get_result(self):
        if not self._result:
            if not self.is_done():
                raise Exception("Job has not finished yet!")
            self._result = self._response_method(self._job_id)
        return self._result

    def show_progress(self):
        self._info.show_progress()

    def get_metrics(self):
        return self._info.get_metrics()

    def __repr__(self):
        return f"""Job(id={self.id}, type={self.job_type}, done={self.done}, childJobIds={self.child_job_ids})"""
