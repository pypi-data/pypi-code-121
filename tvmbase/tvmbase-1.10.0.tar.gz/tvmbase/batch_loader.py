from loguru import logger
from tonclient.types import ParamsOfQueryOperation, ParamsOfBatchQuery, ResultOfQueryCollection

from tvmbase.client import Client
from tvmbase.models.boc_type import BocType
from tvmbase.models.tvm.base import BaseTvm


class BatchLoader:

    def __init__(self, client: Client):
        self.client = client

    async def load(self, data: list[tuple[str, BocType]]) -> list[BaseTvm]:
        logger.debug(f'Loading batch with size {len(data)}...')
        operations = list()
        for idx, boc_type in data:
            tvm_class: BaseTvm = boc_type.value
            query = tvm_class.gql_query(idx)
            operations.append(
                ParamsOfQueryOperation.QueryCollection(params=query)
            )
        params = ParamsOfBatchQuery(operations=operations)
        results = await self.client.net.batch_query(params=params)
        instances = list()
        for (idx, boc_type), result in zip(data, results.results):
            tvm_class: BaseTvm = boc_type.value
            query_result = ResultOfQueryCollection(result)
            instance = await tvm_class.from_query_result(self.client, idx, query_result)
            instances.append(instance)
        return instances
