from tonclient.types import ParamsOfParse, ParamsOfQueryCollection

from tvmbase.client import Client
from tvmbase.models.data import TransactionData
from tvmbase.models.tvm.base import BaseTvm
from tvmbase.utils.attrs_helper import convert_nested


class Transaction(BaseTvm):
    DATA_TYPE = TransactionData

    def __init__(self, idx: str, data: TransactionData):
        super().__init__(idx)
        self.data = data

    @staticmethod
    def gql_query(idx: str) -> ParamsOfQueryCollection:
        return ParamsOfQueryCollection(
            collection='transactions',
            result='boc',
            limit=1,
            filter={'id': {'eq': idx}},
        )

    @classmethod
    async def from_boc(cls, client: Client, boc: str, **kwargs) -> 'Transaction':
        parse_params = ParamsOfParse(boc=boc)
        parsed = await client.boc.parse_transaction(params=parse_params)
        parsed_dict = parsed.parsed
        convert_nested(parsed_dict, TransactionData)
        idx = parsed.parsed['id']
        data = TransactionData(**parsed_dict, **kwargs)
        return cls(idx, data)
