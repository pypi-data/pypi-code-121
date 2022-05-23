from pathlib import Path
from typing import List

import orjson
from redis.asyncio import ConnectionPool

from libq import types
from libq.base import JobStoreSpec
from libq.connections import create_pool


class RedisJobStore(JobStoreSpec):
    jobs_prefix = "store:jobs"

    def __init__(self, conn=None):
        self.conn: ConnectionPool = conn or create_pool()

    async def get(self, jobid: str) -> types.JobPayload:
        data = await self.conn.hget(self.jobs_prefix, jobid)
        data_dict = orjson.loads(data)
        return types.JobPayload(**data_dict)

    async def put(self, jobid: str, job: types.JobPayload):
        data = job.json()
        await self.conn.hset(self.jobs_prefix, mapping={jobid: data})

    async def delete(self, jobid: str) -> bool:
        res = await self.conn.hdel(self.jobs_prefix, jobid)
        if res == 0:
            return False
        return True

    async def list(self) -> List[str]:
        keys = await self.conn.hkeys(self.jobs_prefix)
        return keys


# class FileStore(JobStoreSpec):
#
#     def __init__(self, schedule_file: str):
#         self._jobs = Path(schedule_file)
#
#     async def get(self, jobid)
