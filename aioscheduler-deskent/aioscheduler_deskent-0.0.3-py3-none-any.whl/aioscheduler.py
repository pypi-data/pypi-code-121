import asyncio
import datetime
from dataclasses import dataclass
from typing import Callable, Union, Optional, Coroutine
import logging


logger = logging.getLogger('Scheduler')


@dataclass
class Scheduler:

    def __init__(self):
        self.jobs: list = []

    def add_job(self, job: 'Callable', timestamp: Union[float, int]) -> 'Scheduler':
        """Adds new instance Job to the jobs list and returns instance of itself"""

        self.jobs.append(Job(job_func=job, timestamp=timestamp))

        return self

    async def run(self) -> list:
        """Create tasks for working and run them
        returns list of results for every job"""

        if not self.jobs:
            return []
        tasks: list = [
            asyncio.create_task(job.run_job())
            for job in self.jobs
        ]
        worked_jobs: list = self.jobs[:]
        self._del_worked_jobs(worked_jobs)
        responses = await asyncio.gather(*tasks)
        if not responses:
            return []
        return [await response for response in responses if response]

    def _del_worked_jobs(self, worked_jobs) -> int:
        """Delete worked jobs from the jobs list"""

        for job in worked_jobs:
            try:
                self.jobs.remove(job)
            except ValueError:
                logger.debug("Job remove error")
        return len(worked_jobs)


@dataclass
class Job:
    job_func: 'Callable' = None
    timestamp: Union[float, int] = None

    async def run_job(self) -> Optional['Coroutine']:
        """Run current job after timeout, returns result of job function"""

        current_time = float(datetime.datetime.utcnow().replace(tzinfo=None).timestamp())
        time_to_sleep: float = float(self.timestamp - current_time)
        if time_to_sleep <= 0:
            logger.warning(f"Cannot run job in past time.")
            return
        logger.debug(f"Task added [{self.timestamp}]\tTime to sleep [{time_to_sleep}]")
        try:
            await asyncio.gather(
                asyncio.wait_for(asyncio.sleep(time_to_sleep), time_to_sleep + 1),
                asyncio.sleep(1 / 1000)
            )
        except asyncio.TimeoutError as err:
            logger.error(f'Timeout error: {err}')
        return self.job_func()
