from dataclasses import dataclass
import inspect
import os
from typing import List


@dataclass
class DatabuttonSchedule:
    # Unique identifier
    uid: str
    # The human readable name for the job
    name: str
    # The actual name of the function
    func_name: str
    # Seconds between runs (first run will be at t0 + seconds)
    seconds: float
    # The path to the .py file where the schedule is defined
    filepath: str
    # The name of the module (i.e jobs.schedule)
    module_name: str
    # Should the job be cancelled on failure
    cancel_on_failure: bool = False

    def to_dict(self):
        return self.to_dict()


_schedules: List[DatabuttonSchedule] = []


def repeat_every(seconds: float, name: str = None, cancel_on_failure: bool = False):
    def wrapper(func):
        filepath = os.path.relpath(inspect.getfile(func), os.curdir)
        job_name = name if name is not None else func.__name__
        uid = f"{filepath}-{job_name}"
        _schedules.append(
            DatabuttonSchedule(
                uid=uid,
                name=job_name,
                func_name=func.__name__,
                seconds=seconds,
                filepath=filepath,
                module_name=inspect.getmodule(func).__name__,
                cancel_on_failure=cancel_on_failure,
            )
        )
        return func

    return wrapper
