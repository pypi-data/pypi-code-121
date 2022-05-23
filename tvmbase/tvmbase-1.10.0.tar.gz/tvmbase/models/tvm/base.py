from abc import ABC, abstractmethod
from typing import Any

import attrs
from tonclient.types import ParamsOfQueryCollection, ResultOfQueryCollection

from tvmbase.client import Client


class BaseTvm(ABC):
    DATA_TYPE: type = None

    def __init__(self, idx: str, data: Any = None):
        self.idx = idx
        self.data = data

    @classmethod
    async def from_idx(cls, client: Client, idx: str) -> 'BaseTvm':
        query = cls.gql_query(idx)
        result = await client.net.query_collection(params=query)
        return await cls.from_query_result(client, idx, result)

    @staticmethod
    @abstractmethod
    def gql_query(idx: str) -> ParamsOfQueryCollection:
        pass

    @classmethod
    async def from_query_result(cls, client: Client, idx: str, result: ResultOfQueryCollection) -> 'BaseTvm':
        boc = result.result[0]['boc']
        return await cls.from_boc(client, boc)

    @classmethod
    @abstractmethod
    async def from_boc(cls, client: Client, boc: str, **kwargs) -> 'BaseTvm':
        pass

    @classmethod
    def from_dict(cls, dump: dict) -> 'BaseTvm':
        idx = dump['idx']
        data = dump['data']
        if data is not None:
            data = cls.DATA_TYPE(**data)
        return cls(idx, data)

    def to_dict(self) -> dict:
        data = attrs.asdict(self.data) if self.data is not None else None
        return {
            'idx': self.idx,
            'data': data,
        }

    def __str__(self) -> str:
        return f'{self.__class__.__name__}<{self.idx}>'

    __repr__ = __str__
