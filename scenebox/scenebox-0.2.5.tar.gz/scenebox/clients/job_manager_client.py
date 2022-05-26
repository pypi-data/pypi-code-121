"""Jobs manager client.

Copyright 2020 Caliber Data Labs
"""

#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

import json
import time
from typing import List, NamedTuple, Optional, Union, Callable

import requests

from ..constants import ACK_OK_RESPONSE, JobConstants, JobTags, JobTypes
from ..custom_exceptions import JobError
from ..tools.logger import get_logger
from ..tools.misc import join, retry

DEFAULT_SEARCH_SIZE = 500

# seconds. Note that this determines the minimum job time.
CHECK_JOB_STATUS_INTERVAL = 10

UPDATE_JOB_PROGRESS_STEP = 5

logger = get_logger(__name__)

STATUS_INTERVAL = 30


class Job(NamedTuple):
    id: str
    status: str
    progress: float
    description: str
    stage: str = ""


class JobManagerClient(JobConstants):
    """Client for interacting with the Job Manager."""

    def __init__(
        self,
        asset_manager_url: str,
        auth_token: str,
        job_id: Optional[str] = None,
        asset_type: Optional[str] = None,
        asset_id: Optional[str] = None,
        username: Optional[str] = None,
        job_type: Optional[str] = None,
        notes: Optional[Union[List[str], str]] = None,
        description: Optional[str] = None,
        stage: Optional[str] = None,
        tags: Optional[List[str]] = None,
        user_facing: bool = False,
        task_sync: bool = False,
        resubmittable: bool = False
    ):
        """
        asset_manager_url: URL to asset manager
        auth_token: Auth token to use
        job_id: unique identifier of a job
        asset_type: Type of asset ( used for updating job metadata)
        asset_id: Asset ID (used for updating job metadata)
        username: Username (used for updating job metadata)
        job_type: Type of the job (used for updating job metadata)
        notes: time-history of the events in the job (started at what time, queued at what time) (used for updating job metadata)
        description: the description of the job (used for updating job metadata)
        stage: Job stage (used for updating job metadata)
        ttl: job's time to live in seconds
        sync_interval: Time interval to wait before checking if timeout > TTL or job failure,
        """

        self.jobs_api_url = join(asset_manager_url, "jobs")
        self.auth_token = auth_token
        self.raise_on_failure = False

        if not job_id:
            tags = tags or []
            if user_facing:
                tags.append(JobTags.USER_FACING)

            if resubmittable:
                tags.append(JobTags.RESUBMITTABLE)

            job_id = self.create_job(
                asset_type,
                asset_id,
                username,
                job_type,
                notes,
                description,
                stage,
                tags,
                task_sync
            )

        self.job_id = job_id
        self.last_progress = 0.0
        self.last_stage = None
        self.last_status = JobConstants.STATUS_INITIALIZED

    def create_job(
            self,
            asset_type: str,
            asset_id: str,
            username: str,
            job_type: str,
            notes: list,
            description: str,
            stage: str,
            tags: List[str],
            task_sync: bool
    ) -> str:

        description = description or ''

        if job_type not in JobTypes.VALID_TYPES:
            raise JobError("Job {} requested by {} - invalid job type = {}".format(description, username, job_type))

        asset_id = asset_id or 'undefined'

        json_payload = {
            "asset_type": asset_type,
            "asset_id": asset_id,
            "user": username,
            "job_type": job_type or '',
            "notes": notes or [],
            "description": description,
            "stage": stage or '',
            "tags": tags or [],
            "task_sync": task_sync
        }
        params = self.add_asset_manager_params()

        url = self.get_jobs_url("add/")
        resp = requests.post(url, json=json_payload, params=params)
        if not resp.ok:
            raise JobError(
                "Could not create the job ::: {} -- {}".format(
                    resp.reason, resp.content
                )
            )
        else:
            return resp.json()["job_id"]

    def queue(self):
        url = self.get_jobs_url('queue/{}'.format(self.job_id))
        params = self.add_asset_manager_params()
        resp = requests.put(url, params=params)
        if not resp.ok:
            return self.__job_error(
                "Could not queue the job ::: {} -- {}".format(
                    resp.reason, resp.content)
            )
        else:
            return resp.json()

    def run(self,
            cpu_core: Optional[int] = None,
            hostname: Optional[str] = None):

        url = self.get_jobs_url('run/{}'.format(self.job_id))

        json_payload = {}
        if cpu_core is not None:
            json_payload["cpu_core"] = cpu_core
        if hostname is not None:
            json_payload["hostname"] = hostname

        params = self.add_asset_manager_params()
        resp = requests.put(url, params=params, json=json_payload)
        if not resp.ok:
            return self.__job_error(
                "Could not run the job ::: {} -- {}".format(
                    resp.reason, resp.content)
            )
        else:
            return resp.json()

    def finish(self):
        if self.get_status() == JobConstants.STATUS_FINISHED:
            return
        url = self.get_jobs_url('finish/{}'.format(self.job_id))
        params = self.add_asset_manager_params()
        resp = requests.put(url, params=params)
        if not resp.ok:
            return self.__job_error(
                "Could not finish the job ::: {} -- {}".format(
                    resp.reason, resp.content
                )
            )
        else:
            return resp.json()

    def abort(self,
              revoke_celery_job: bool = False,
              error_string: str = '',
              exception: Optional[Exception] = None):
        if exception is not None:
            error_string = repr(exception)
        else:
            error_string = str(error_string)[0:1024]
        self.update_stage(stage="Error :{}".format(error_string))
        if self.get_status() == JobConstants.STATUS_ABORTED:
            return
        url = self.get_jobs_url('abort/{}'.format(self.job_id))
        params = {'error_string': error_string,
                  'revoke': revoke_celery_job}
        params = self.add_asset_manager_params(params)
        resp = requests.put(url, params=params)
        if not resp.ok:
            return self.__job_error(
                "Could not abort the job ::: {} -- {}".format(
                    resp.reason, resp.content)
            )
        else:
            return resp.json()

    def append_note(self, note):
        url = self.get_jobs_url('append_note/{}'.format(self.job_id))
        params = {'note': note}
        params = self.add_asset_manager_params(params)
        resp = requests.put(url, params=params)
        if not resp.ok:
            return self.__job_error(
                "Could not append_note to the job ::: {} -- {}".format(
                    resp.reason, resp.content
                )
            )
        else:
            return resp.json()

    def update_meta(self, key, value):
        url = self.get_jobs_url('meta/{}'.format(self.job_id))
        data = {'key': key, 'value': value}
        params = self.add_asset_manager_params()
        resp = requests.put(url, json=data, params=params)
        if not resp.ok:
            return self.__job_error(
                "Could not update meta of the job ::: {} -- {}".format(
                    resp.reason, resp.content
                )
            )
        else:
            return resp.json()

    def get_notes(self) -> List[str]:
        return self.get_comprehensive_status().get("notes", [])

    def update_stage(self, stage):
        self.last_stage = stage
        url = self.get_jobs_url('stage/{}'.format(self.job_id))
        params = {'stage': stage}
        params = self.add_asset_manager_params(params)
        resp = requests.put(url, params=params)
        if not resp.ok:
            return self.__job_error(
                "Could not update stage of the job ::: {} -- {}".format(
                    resp.reason, resp.content
                )
            )
        else:
            return resp.json()

    @retry(Exception, logger=logger, initial_wait=1)
    def get_status(self) -> str:
        url = self.get_jobs_url('status/{}'.format(self.job_id))
        params = self.add_asset_manager_params()
        resp = requests.get(url, params=params)
        if not resp.ok:
            self.__job_error(
                "Could not get status of the job ::: {} -- {}".format(
                    resp.reason, resp.content))
            return self.last_status
        else:
            status = resp.json()["status"]
            self.last_status = status
            return status

    @retry(Exception, logger=logger, initial_wait=1)
    def get_comprehensive_status(self) -> dict:
        url = self.get_jobs_url('comprehensive_status/{}'.format(self.job_id))
        params = self.add_asset_manager_params()
        resp = requests.get(url, params=params)
        if not resp.ok:
            raise JobError(
                "Could not get status of the job ::: {} -- {} -- with auth token: {}".format(
                    resp.reason, resp.content, self.auth_token))
        return resp.json()

    @retry(Exception, logger=logger, initial_wait=1)
    def get_progress(self) -> float:
        url = self.get_jobs_url('progress/{}'.format(self.job_id))
        params = self.add_asset_manager_params()
        resp = requests.get(url, params=params)
        if not resp.ok:
            self.__job_error(
                "Could not get progress the job ::: {} -- {}".format(
                    resp.reason, resp.content
                )
            )
            return self.last_progress
        else:
            self.last_progress = resp.json()["progress"]
            return self.last_progress

    def update_progress(self,
                        progress: float,
                        raise_on_abort_canceled: bool = False,
                        message: str = None,
                        force_update=False):
        """
        Args:
            progress (float): percentage of job progress
            raise_on_abort_canceled (bool): raise JobError if job is canceled or aborted when this is True
            message: status update string
            force_update: should force update regardless of the last_progress status
        """
        if raise_on_abort_canceled:
            job_status = self.get_status()
            if job_status in {JobConstants.STATUS_ABORTED}:
                raise JobError('Job is {}'.format(job_status))

        if (progress - self.last_progress) > UPDATE_JOB_PROGRESS_STEP or progress >= 100.0\
                or (self.last_stage != message) or force_update:
            self.last_progress = progress
            params = {'progress': round(progress, 2)}
            if message is not None:
                self.update_stage(message)

            url = self.get_jobs_url('progress/{}'.format(self.job_id))
            params = self.add_asset_manager_params(params)
            resp = requests.put(url, params=params)
            if not resp.ok:
                return self.__job_error(
                    "Could not update_progress of the job ::: {} -- {}".format(
                        resp.reason, resp.content
                    )
                )
            else:
                return resp.json()

    def resubmit(self):
        """Resubmit a job."""

        url = self.get_jobs_url('resubmit/{}'.format(self.job_id))
        params = self.add_asset_manager_params()
        resp = requests.put(url, params=params)
        if not resp.ok:
            raise JobError(
                "Could not resubmit the job ::: {} -- {}".format(
                    resp.reason, resp.content
                )
            )
        return resp.json()

    def get_jobs_url(self, route):
        url = join(self.jobs_api_url, route)
        return url

    def add_asset_manager_params(self, params_dict=None):
        if params_dict is None:
            params_dict = {}
        if self.auth_token:
            params_dict["token"] = self.auth_token
        return params_dict

    def add_child_job(self, job_id: str):
        self.update_meta(key="child_job_ids", value=[job_id])

    def abort_task(self,task_id: str):
        url = self.get_jobs_url(f"query_task/{task_id}/abort")
        params = self.add_asset_manager_params()
        return requests.get(url, params=params).json()

    def __job_error(self, message: str):
        error_message = "job_id {} -- {} -- token {}".format(self.job_id, message, self.auth_token)
        if self.raise_on_failure:
            raise JobError(error_message)
        else:
            logger.error(msg=error_message)
            return {"status": "job {} failed with {}".format(self.job_id, message)}

    def get_job(self) -> Job:
        """Get the job_manager_client.Job object associated with the provided job ID.

        Can be a currently executing or finished Job.

        Parameters
        ----------
        job_id:
            The job ID associated with the Job of interest.

        Returns
        -------
        Job
            Job object with the job id ``job_id``.

        """
        comprehensive_status = self.get_comprehensive_status()
        return Job(
            status=comprehensive_status.get("status"),
            id=self.job_id,
            progress=comprehensive_status.get("progress", 0.0),
            description="",
            stage=comprehensive_status.get("stage")
        )

    def wait_for_completion(self,
                            increments_sec: int = 10,
                            enable_max_wait: bool = False,
                            max_wait_sec: int = 300,
                            progress_callback: Optional[Callable] = None):
        """Wait for a job to complete.

        Input a max waiting time before an unfinished job throws an Exception.  Choose to either poll while a job is in
        progress, or enact a callable function ``progress_callback()`` with every increment set by ``increments_sec``.

        Parameters
        ----------
        job_id:
            The ID of the job in progress.
        increments_sec:
            The amount of time to poll in between checking job status and calling progress_callback().
        enable_max_wait:
            If True, immediately throws an Exception.  Intended for use when there is an external timing constraint.
            Otherwise, does nothing.
        max_wait_sec:
            The maximum amount of time to wait for a job to finish before throwing an exception.  Measured in seconds.
        progress_callback:
            Callback function to log the progress of the inference job. The callback should accept a parameter of type
            float for progress and str for progress message.

        Raises
        ------
        JobError
            If job encounters an error, and could not complete.
            If job does not finish after ``max_wait_sec`` seconds.

        """
        # progress callable should take progress as an input and do "something" with it

        elapsed_time = 0
        try:
            while not enable_max_wait or elapsed_time < max_wait_sec:
                elapsed_time += increments_sec
                job = self.get_job()
                if progress_callback:
                    progress_callback(job.progress, job.stage)
                logger.info(
                    "job_id {:40.40s}|Status:{:12.12s}|Progress:{:6.1f} Elapsed Time: {:5d} sec\r".format(
                        self.job_id,
                        job.status,
                        job.progress,
                        elapsed_time))
                if job.status == JobConstants.STATUS_FINISHED:
                    logger.info(150 * "-" + "\r")
                    return
                elif job.status in {JobConstants.STATUS_ABORTED}:
                    job_notes = self.get_notes()
                    raise JobError(
                        'Job {} encountered error with status {} with notes::: {}'.format(
                            self.job_id, job.status, job_notes))
                else:
                    time.sleep(increments_sec)
        except KeyboardInterrupt as e:
            url = self.get_jobs_url('jobs/cancel/{}'.format(self.job_id))
            resp = requests.put(url)
            if not resp.ok:
                logger.error("Could not interrupt running job {} because {}".format(self.job_id,
                                                                                    resp.content))
            else:
                raise JobError("Job {} terminated by user".format(self.job_id))

        raise JobError(
            "Job {} is not finished after {} seconds".format(
                self.job_id, max_wait_sec))


def wait_for_jobs(
        job_ids: List[str],
        asset_manager_url: str,
        auth_token: str,
        timeout: Optional[int] = None,
        raise_on_error: bool = False,
        progress_callback: Optional[Callable] = None,
):
    failed_enrichment_jobs = set()
    successful_job_ids = set()
    logger.info("Waiting for {} jobs to finish:: {}".format(
        len(job_ids), job_ids[0:10]))

    # Wait for all enrichment tasks to finish
    job_ids_to_clients = dict(
        [
            (
                job_id,
                JobManagerClient(
                    job_id=job_id,
                    asset_manager_url=asset_manager_url,
                    auth_token=auth_token
                )
            )
            for job_id in job_ids
        ]
    )
    logger.info("jobs being done: {}".format(
        job_ids_to_clients))
    t1 = time.time()
    finished_jobs = set()
    job_id_to_progress_dict = {}

    while True:
        for job_id, job_manager_client in job_ids_to_clients.items():
            job_status = job_manager_client.get_status()
            job_id_to_progress_dict[job_id] = job_manager_client.get_progress()

            if job_status in {
                JobManagerClient.STATUS_FINISHED,
                JobManagerClient.STATUS_ABORTED}:
                if job_status == JobManagerClient.STATUS_FINISHED:
                    successful_job_ids.add(job_id)
                    logger.info('Job {} finished'.format(job_id))
                elif job_status == JobManagerClient.STATUS_ABORTED:
                    failed_enrichment_jobs.add(job_id)
                    logger.info('Job {} failed'.format(job_id))
                    if raise_on_error:
                        raise JobError(
                            "Job {} encountered failure".format(job_id))
                finished_jobs.add(job_id)

        # Update callback with progress
        if progress_callback:
            progress_callback(job_id_to_progress_dict)

        job_ids_to_clients = {
            k: v for k,
                     v in job_ids_to_clients.items() if k not in finished_jobs}

        if len(job_ids_to_clients) == 0:
            break
        else:
            logger.info(
                "Waiting for {} jobs to finish:: {}".format(
                    len(job_ids_to_clients), list(
                        job_ids_to_clients.keys())[
                                             0:5]))

            time.sleep(CHECK_JOB_STATUS_INTERVAL)
            if timeout and time.time() - t1 > timeout:
                raise TimeoutError(
                    "Waiting for {} jobs exceeded timeout of {}s".format(
                        len(job_ids), timeout))

    return {
        "successful": len(list(successful_job_ids)),
        "failed": len(list(failed_enrichment_jobs))
    }
