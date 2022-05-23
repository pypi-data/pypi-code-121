from typing import Any, Dict, List, Optional

import orjson

from libq.types import Command, JobGenericFail, JobPayload


def command_serializer(cmd: str, *, key: str, public: str = "all") -> str:
    final = f"{key}:{cmd}:{public}"
    return final


def command_deserializer(cmd: str):
    key, cmd, public = cmd.split(":")
    return Command(key=key, action=cmd, public=public)


def dict_serializer(data: Dict[str, Any]) -> str:
    _data = orjson.dumps(data)
    return _data


def dict_deserializer(data: str) -> Dict[str, Any]:
    return orjson.loads(data)


def job_serializer(job: JobPayload) -> str:
    return job.json()


def job_deserializer(data: str) -> JobPayload:
    _data = orjson.loads(data)
    return JobPayload(**_data)


def generic_fail_serializer(job: JobGenericFail) -> str:
    return job.json()


def generic_fail_deserializer(data: str) -> JobGenericFail:
    _data = orjson.loads(data)
    return JobGenericFail(**_data)
