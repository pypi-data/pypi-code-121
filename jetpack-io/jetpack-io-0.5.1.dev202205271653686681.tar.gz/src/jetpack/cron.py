"""
Submodule for scheduling and running functions as Kubernetes CronJobs
"""
import os
from typing import Any, Callable, List, Optional

from schedule import Job as ScheduleJob  # Use this to whitelist what we allow
from schedule import every

from jetpack.config import _instrumentation, _symbols
from jetpack.proto.runtime.v1alpha1 import remote_pb2

cronjob_suffix = os.environ.get("JETPACK_CRONJOB_SUFFIX", "-missing-suffix")


def repeat(
    repeat_pattern: Optional[ScheduleJob] = None, schedule: Optional[str] = None
) -> Callable[..., Any]:
    """Decorate a function to run it as a Kubernetes CronJob.

    The decorated function will be registered with the runtime, which will create a
    CronJob object on your cluster, with the schedule set to match the repeat_pattern
    or schedule provided as an argument.

    Typical Examples:

        # Run my_function daily

        @cron.repeat(schedule="0 0 * * *")
        def my_function():

        # Run my_function every 2 hours

        @cron.repeat(cron.every(2).hours)
        def my_function():

    Args:
        repeat_pattern (schedule.Job): Defines the CronJob schedule using the `schedule.Job` API
        schedule (str): crontab format (e.g. 1 2 3 * *)

    Returns:
        Callable[..., Any]

    """

    def wrapper(func: Callable[..., Any]) -> Any:
        if (schedule and repeat_pattern) or (not schedule and not repeat_pattern):
            raise Exception(
                "Only exactly 1 of (repeat_pattern, schedule) can be passed in"
            )
        name = _symbols.get_symbol_table().register(
            func, schedule=schedule, repeat_pattern=repeat_pattern
        )
        _instrumentation.get_tracer().cronjob_loaded(
            name, schedule=schedule, repeat_pattern=repeat_pattern
        )
        return func

    return wrapper


def get_jobs() -> List[remote_pb2.CronJob]:
    cron_jobs = []
    for cronjob in _symbols.get_symbol_table().get_cronjobs():
        schedule_job = cronjob.repeat_pattern

        target_time = ""
        target_day_of_week = remote_pb2.DayOfWeek.UNKNOWN_DAY
        unit = remote_pb2.Unit.UNKNOWN_UNIT
        interval = 0
        schedule_rule = ""

        if schedule_job:
            unit = remote_pb2.Unit.Value(schedule_job.unit.upper())
            interval = schedule_job.interval
            if schedule_job.at_time is not None:
                target_time = schedule_job.at_time.isoformat()
            if schedule_job.start_day is not None:
                target_day_of_week = remote_pb2.DayOfWeek.Value(
                    schedule_job.start_day.upper()
                )
        elif cronjob.schedule:
            schedule_rule = cronjob.schedule
        else:
            raise Exception("Expected repeat_pattern or schedule to be set")

        cron_jobs.append(
            remote_pb2.CronJob(
                qualified_symbol=cronjob.name,
                target_time=target_time,
                target_day_of_week=target_day_of_week,
                unit=unit,
                interval=interval,
                schedule_rule=schedule_rule,
            )
        )

    return cron_jobs


def pretty_print(self: remote_pb2.CronJob) -> str:
    s = f"Function: {self.qualified_symbol}"
    s += f"\nInterval: every {self.interval} {remote_pb2.Unit.Name(self.unit).lower()}"
    if self.target_time:
        s += f"\n at {self.target_time}"
    if self.target_day_of_week:
        s += f"\n on {remote_pb2.DayOfWeek.Name(self.target_day_of_week).capitalize()}"
    return s
