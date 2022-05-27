import asyncio
import datetime
from dataclasses import dataclass
from typing import Callable, Union, Optional, Coroutine
import logging


logger = logging.getLogger('Scheduler')


@dataclass
class Scheduler:

    job_func: 'Callable' = None
    timestamp: Union[float, int] = None

    def add_job(self, job: 'Callable', timestamp: Union[float, int]):
        """Adds new instance Job to the jobs list and returns instance of itself"""

        self.job_func = job
        self.timestamp = timestamp

        return self

    async def run(self) -> Optional['Coroutine']:
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
        result = self.job_func()
        try:
            return await result
        except TypeError:
            return result
