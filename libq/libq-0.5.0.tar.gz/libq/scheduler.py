import asyncio
from datetime import timedelta
from time import time
from typing import List, Optional

from croniter import croniter
from redis.asyncio import ConnectionPool

from libq import defaults, types
from libq.base import JobStoreSpec
from libq.connections import create_pool
from libq.logs import logger
from libq.queue import Queue
from libq.utils import generate_random, now_dt, poll, to_unix


class Scheduler:

    def __init__(self, job_store: JobStoreSpec, *,
                 conn=None,
                 partition=None,
                 expire_lock=10,
                 interval=30):
        """
        A Scheduler that has interval and cron syntax for scheduling jobs
        It only stores the job reference, and it needs a Store based on the
        JobStoreSpec to get the real payload to enqueue the job.
        """
        self.conn: ConnectionPool = conn or create_pool()
        self.partition = partition or defaults.SCHEDULER_PARTITION
        self._expire_lock = expire_lock
        self._lock_acquired = False
        self._interval = interval
        self.store: JobStoreSpec = job_store

    @property
    def lock_key(self):
        return f"{types.Prefixes.scheduler_lock.value}{self.partition}"

    @property
    def jobs_key(self):
        return f"{types.Prefixes.scheduler_jobs.value}{self.partition}"

    def get_repeat_key(self, jobid: str) -> str:
        return f"{types.Prefixes.schedule_job_repeat.value}{jobid}"

    async def acquire_lock(self):
        _id = generate_random()
        expire = self._interval + self._expire_lock
        self._lock_acquired = await self.conn.set(
            self.lock_key, _id, ex=expire, nx=True)
        logger.debug("Lock acquired")
        return self._lock_acquired

    async def remove_lock(self):
        if self._lock_acquired:
            await self.conn.delete(self.lock_key)
            self._lock_acquired = False
            logger.debug("Lock released")

    async def interval(self, jobid: str, schedule_time, interval: int,
                       repeat: Optional[int] = None):
        key = types.Prefixes.scheduler_jobs
        await self.conn.zadd(key, {jobid: schedule_time})

    async def _check_repeat(self, jobid, repeat) -> bool:
        repeat_key = self.get_repeat_key(jobid)
        do_the_job = True
        if repeat:
            repeated = await self.conn.get(repeat_key)
            if not repeated:
                repeated = 0
            repeated = int(repeated)
            if repeated <= repeat:
                await self.conn.incr(repeat_key)
            else:
                do_the_job = False
        return do_the_job

    async def get_expired(self) -> List[str]:
        now = now_dt() + timedelta(seconds=10)
        end = to_unix(now)
        start = 0
        results = await self.conn.zrange(self.jobs_key, start, end)

        return results

    async def remove_job(self, jobid: str):
        repeat_key = self.get_repeat_key(jobid)
        async with self.conn.pipeline() as pipe:
            pipe.delete(repeat_key)
            pipe.zrem(self.jobs_key, jobid)
            await pipe.execute()

    async def enqueue_job(self, jobid: str):
        """
        Put the jobid into a sorted set.
        For now it uses the original jobid to enqueue the task
        this implies that if the same job is already running it will not
        be scheduled.
        """
        job = await self.store.get(jobid=jobid)
        schedule: types.JobSchedule = job.schedule
        if schedule:
            do_the_job = await self._check_repeat(jobid, schedule.repeat)
            if schedule.interval and do_the_job:
                q = Queue(job.queue, conn=self.conn)
                # execid = generate_random()
                logger.info(f"Enqueing job {jobid}")
                await q.send_job(jobid, payload=job)
                next_run = now_dt() + timedelta(seconds=job.schedule.interval)
                await self.conn.zadd(self.jobs_key, {jobid: to_unix(next_run)})
            elif schedule.cron and do_the_job:
                q = Queue(job.queue, conn=self.conn)
                # execid = generate_random()
                logger.info(f"Enqueing job {jobid}")
                await q.send_job(jobid, payload=job)
                iter_ = croniter(schedule.cron, now_dt())
                next_run = iter_.get_next()
                await self.conn.zadd(self.jobs_key, {jobid: next_run})

            else:
                await self.remove_job(jobid)
                logger.info(f"Jobid {jobid} removed")
        else:
            await self.remove_job(jobid)
            logger.info(f"Jobid {jobid} removed")

    async def get_enqueued(self):
        return await self.conn.zrange(self.jobs_key, 0, -1)

    async def run(self):
        logger.info("Starting scheduler")
        # self.main_task = self.loop.create_task(self.main())
        async for _ in poll(self._interval):
            lock = await self.acquire_lock()
            if lock:
                jobs_id = await self.get_expired()
                for j in jobs_id:
                    await self.enqueue_job(j)
                await self.remove_lock()
            else:
                logger.debug("Lock already taken - skipping run")
