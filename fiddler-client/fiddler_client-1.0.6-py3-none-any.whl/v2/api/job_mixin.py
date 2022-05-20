import time
from http import HTTPStatus
from typing import List

from fiddler.utils import logging
from fiddler.v2.schema.job import JobStatus
from fiddler.v2.utils.exceptions import handle_api_error_response
from fiddler.v2.utils.response_handler import JobResponseHandler

logger = logging.getLogger(__name__)


class JobMixin:
    @handle_api_error_response
    def get_job(self, uuid: str) -> JobResponseHandler:
        """
        Get details about a job

        :params uuid: Unique identifier of the job to get the details of
        :returns: JobResponseHandler object containing details
        """
        response = self.client.jobs._(uuid).get()
        if response.status_code == HTTPStatus.OK:
            return JobResponseHandler(response)
        else:
            # @TODO we should throw error here instead of logging
            logger.info(f'Response status code: {response.status_code}')
            logger.info(response.body)

    def poll_job(self, uuid: str, interval: int = 3) -> JobResponseHandler:
        """
        Poll an ongoing job. This method will keep polling until a job has SUCCESS, FAILURE, RETRY, REVOKED status.
        Will return a JobResponseHandler object once the job has ended.

        :params uuid: Unique identifier of the job to keep polling
        :params interval: Interval in sec between two subsequent poll calls. Default is 1sec
        :returns: JobResponseHandler object containing job details.
        """
        job = self.get_job(uuid)
        # @TODO: Set max iteration limit?
        while job.status in [JobStatus.PENDING, JobStatus.STARTED]:
            # @TODO: show proper message
            logger.info(
                f'JOB UUID: {uuid} status: {job.status} Progress: {job.progress}'
            )

            time.sleep(interval)
            job = self.get_job(uuid)

        if job.status == JobStatus.FAILURE:
            logger.error(
                f"JOB UUID: {uuid} failed with error message '{job.error_message}'"
            )

        logger.info(f'JOB UUID: {uuid} status: {job.status} Progress: {job.progress}')
        return job

    @staticmethod
    def get_task_results(job: JobResponseHandler) -> List[str]:
        results: List[str] = []
        for task_id, extra_info in job.extras.items():
            if not extra_info['result']:
                continue
            results.append(
                f'JOB UUID: {job.uuid} task id: {task_id} result: {extra_info["result"]}'
            )
        return results
