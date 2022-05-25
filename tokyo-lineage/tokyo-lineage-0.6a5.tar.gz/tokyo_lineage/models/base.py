import attr

@attr.s
class BaseTask:
    task_id: str = attr.ib(init=True, default=None)
    operator_name: str = attr.ib(init=True, default=None)


@attr.s
class BaseJob:
    job_id: str = attr.ib(init=True, default=None)