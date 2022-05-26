import asyncio
import datetime
from dataclasses import dataclass
from typing import Callable, Union
import logging

logger = logging.getLogger('Scheduler')


@dataclass
class Job:
    job_func: 'Callable' = None
    timestamp: Union[float, int] = None

    async def run_job(self):
        time_to_sleep: float = float(self.timestamp - datetime.datetime.now().timestamp())
        logger.debug(f"Task added [{self.timestamp}]\tTime to sleep [{time_to_sleep}]")
        try:
            await asyncio.gather(
                asyncio.wait({asyncio.sleep(time_to_sleep)}),
                asyncio.sleep(1 / 1000)
            )
        except asyncio.TimeoutError:
            print('timeout!')
        return self.job_func()


@dataclass
class MyScheduler:

    def __init__(self):
        self.jobs: list = []

    def add_job(self, job: 'Callable', timestamp: Union[float, int]):
        self.jobs.append(Job(job_func=job, timestamp=timestamp))

        return self

    def _del_worked_jobs(self, worked_jobs):
        for job in worked_jobs:
            try:
                self.jobs.remove(job)
            except ValueError:
                logger.debug("Job remove error")

    async def run(self):
        if not self.jobs:
            return
        tasks: list = [
            asyncio.create_task(job.run_job())
            for job in self.jobs
        ]
        worked_jobs: list = self.jobs[:]
        self._del_worked_jobs(worked_jobs)
        responses = await asyncio.gather(*tasks)
        results = [await response for response in responses]

        return results
