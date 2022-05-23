from tonclient.types import ParamsOfParse, ParamsOfQueryCollection, ResultOfQueryCollection

from tvmbase.client import Client
from tvmbase.models.data import MessageData
from tvmbase.models.tvm.base import BaseTvm


class Message(BaseTvm):
    DATA_TYPE: type = MessageData

    def __init__(self, idx: str, data: MessageData):
        super().__init__(idx)
        self.data = data

    @staticmethod
    def gql_query(idx: str) -> ParamsOfQueryCollection:
        return ParamsOfQueryCollection(
            collection='messages',
            result='boc created_at dst_transaction { id } src_transaction { id }',
            limit=1,
            filter={'id': {'eq': idx}},
        )

    @classmethod
    async def from_query_result(cls, client: Client, idx: str, result: ResultOfQueryCollection) -> 'Message':
        result_dict = result.result[0]
        boc = result_dict['boc']
        created_at = result_dict['created_at']
        dst_transaction_id = cls._get_id(result_dict, 'dst_transaction')
        src_transaction_id = cls._get_id(result_dict, 'src_transaction')
        return await cls.from_boc(
            client,
            boc,
            created_at=created_at,
            dst_transaction_id=dst_transaction_id,
            src_transaction_id=src_transaction_id,
        )

    @staticmethod
    def _get_id(result_dict: dict, key: str) -> str:
        data = result_dict.get(key)
        if isinstance(data, dict):
            return data.get('id')

    @classmethod
    async def from_boc(cls, client: Client, boc: str, **kwargs) -> 'Message':
        parse_params = ParamsOfParse(boc=boc)
        parsed = await client.boc.parse_message(params=parse_params)
        idx = parsed.parsed['id']
        created_at = parsed.parsed.pop('created_at', None)
        assert 'created_at' not in kwargs or created_at is None or created_at == kwargs['created_at'], \
            f'Different created at time in message {idx}'
        data = MessageData(**parsed.parsed, **kwargs)
        return cls(idx, data)
