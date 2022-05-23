from abc import ABC, abstractmethod
from typing import List
from libq import types


class JobStoreSpec(ABC):

    @abstractmethod
    async def get(self, jobid: str) -> types.JobPayload:
        pass

    @abstractmethod
    async def put(self, jobid: str, job: types.JobPayload):
        pass

    @abstractmethod
    async def delete(self, jobid: str) -> bool:
        pass

    @abstractmethod
    async def list(self) -> List[str]:
        pass
