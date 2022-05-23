from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Prefixes(Enum):
    ns = "sq"
    job = "sq:job::"
    job_in_progress = "sq:job:running::"
    # queue = "sq:q::"
    # queue_info = "sq:q:info::"
    queue_jobs = "sq:q:jobs::"
    queue_running = "sq:q:running::"
    queue_cancelled = "sq:q:cancelled::"
    queue_failed = "sq:q:failed::"
    queue_complete = "sq:q:complete::"
    queue_workers = "sq:q:workers::"
    queues_list = "sq:q:queues"
    queues_commands = "sq:q:cmd::"
    scheduler_lock = "sq:sch:lock::"
    scheduler_jobs = "sq:sch:jobs::"
    schedule_job_repeat = "sq:sch:repeat::"
    worker = "sq:w::"
    workers_list = "sq:workers"


class JobStatus(Enum):
    not_found = -1
    created = 0
    queued = 1
    running = 2
    retrying = 3
    canceled = 4
    failed = 5
    complete = 6


class JobResult(BaseModel):
    execid: str
    func_name: str
    success: bool
    status: str
    qname: str
    elapsed: float
    started_ts: Optional[float] = None
    func_result: Optional[Dict[str, Any]] = None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class JobGenericFail(BaseModel):
    execid: str
    error: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class JobSchedule(BaseModel):
    interval: Optional[int] = None
    cron: Optional[str] = None
    repeat: Optional[int] = None
    start_now: bool = False


class JobPayload(BaseModel):
    func_name: str
    timeout: int
    background: bool = False
    params: Dict[str, Any] = {}
    result_ttl: int = 60 * 5
    status: int
    queue: str
    created_ts: int
    max_retry: int = 3
    retries: int = 0
    job_id: Optional[str] = None
    started_ts: Optional[float] = None
    job_result: Optional[JobResult] = None
    schedule: Optional[JobSchedule] = None

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class JobRef(BaseModel):
    execid: str
    qname: str


class WorkerInfo(BaseModel):
    id: str
    birthday: str
    last_job: str
    queues: List[str]
    completed: int
    failed: int
    running: int
    tasks_names: List[str]
    metadata: Optional[Dict[str, Any]] = None


class Command(BaseModel):
    key: str
    action: str
    public: str


class PubSubMsg(BaseModel):
    type: str
    pattern: Any
    channel: str
    data: str


@dataclass
class FunctionResult:
    error: bool
    error_msg: Optional[str] = None
    func_result: Optional[Dict[str, Any]] = None

    def json(self) -> str:
        return orjson.dumps(dict(error=self.error, error_msg=self.error_msg,
                                 func_result=self.func_result))
