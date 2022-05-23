import asyncio
import json
from datetime import datetime
from typing import Any, Dict, Optional, Union

from redis.asyncio import ConnectionPool, Redis

from libq import defaults, errors
from libq.logs import logger
from libq.types import JobPayload, JobRef, JobResult, JobSchedule, JobStatus, Prefixes
from libq.utils import now_secs, poll


class Job:

    def __init__(self, id: str, *, conn: Redis, payload=None):
        self._id = id
        self.conn = conn
        self._status: int = JobStatus.not_found.value
        if payload:
            self._status = payload.status
        self._payload: JobPayload = payload

    @property
    def execid(self) -> str:
        return f"{Prefixes.job.value}{self._id}"

    @property
    def ref(self) -> JobRef:
        return JobRef(
            execid=self._id, qname=self._payload.queue
        )

    @property
    def status(self) -> str:
        return JobStatus(self._status).name

    @status.setter
    def status(self, s: int):
        self._status = JobStatus(s).value
        if self._payload:
            self._payload.status = s

    @property
    def success(self) -> bool:
        success = False
        if self._status == JobStatus.complete.value:
            success = True
        return success

    @property
    def failed(self) -> Union[bool, None]:
        failed = None
        if self._status == JobStatus.failed.value:
            failed = True
        return failed

    async def fetch(self) -> JobPayload:
        rsp = await self.conn.get(self.execid)
        if not rsp:
            raise errors.JobNotFound(self._id)

        job = JobPayload(**json.loads(rsp))
        self._payload = job
        self.status = JobStatus(job.status).value
        return job

    async def update(self, ttl=None):
        _ttl = self._payload.timeout or ttl
        await self.conn.setex(f"{Prefixes.job.value}{self._id}",
                              _ttl,
                              self._payload.json())

    async def mark_complete(self, result: Optional[Dict[str, Any]] = None):
        self.status = JobStatus.complete.value
        status = self.status

        now = datetime.utcnow().timestamp()
        elapsed = self._payload.started_ts - now
        job_res = JobResult(
            execid=self._id,
            func_name=self._payload.func_name,
            success=self.success,
            status=status,
            qname=self._payload.queue,
            elapsed=elapsed,
            started_ts=self._payload.started_ts,
            func_result=result)
        self._payload.job_result = job_res
        await self.update(self._payload.result_ttl)

    async def mark_running(self):
        self.status = JobStatus.running.value
        await self.update()

    async def mark_failed(self, error=None):
        self.status = JobStatus.failed.value
        now = datetime.utcnow().timestamp()
        elapsed = self._payload.started_ts - now

        job_res = JobResult(
            execid=self._id,
            func_name=self._payload.func_name,
            success=False,
            status=self.status,
            qname=self._payload.queue,
            elapsed=elapsed,
            started_ts=self._payload.started_ts,
            func_result=error)
        self._payload.job_result = job_res

        await self.update()

    async def mark_retry(self) -> bool:
        retries = self._payload.retries
        max_retries = self._payload.max_retry
        logger.debug(
            f"Retry #{retries + 1} of {max_retries } for {self.execid}")
        if retries < max_retries - 1:
            self._payload.retries += 1
            self.status = JobStatus.retrying.value
            await self.update()
            return True
        return False

    async def mark_canceled(self):
        self.status = JobStatus.canceled.value
        await self.update()

    @property
    def result(self) -> Union[JobResult, None]:
        if self._payload:
            return self._payload.job_result
        return None

    async def get_result(self, timeout: Optional[int] = None,
                         *,
                         poll_delay: float = 0.5,
                         ) -> Union[JobResult, None]:
        async for delay in poll(poll_delay):
            job = await self.fetch()
            if job.job_result:
                return job.job_result
            if timeout is not None and delay > timeout:
                raise asyncio.TimeoutError()

        return None

    @staticmethod
    def create_payload(func_name: str, *,
                       params=None,
                       queue=defaults.QUEUE_NAME,
                       timeout=defaults.JOB_TIMEOUT,
                       background=False,
                       interval=None,
                       cron=None,
                       repeat=None,
                       ) -> JobPayload:
        _params = params or {}
        created_ts = int(now_secs())
        sche = None
        status = JobStatus.created.value
        if interval:
            sche = JobSchedule(interval=interval, repeat=repeat)
        elif cron:
            sche = JobSchedule(cron=cron, repeat=repeat)

        job = JobPayload(
            func_name=func_name,
            params=_params,
            queue=queue,
            status=status,
            created_ts=created_ts,
            timeout=timeout,
            schedule=sche
        )
        return job
