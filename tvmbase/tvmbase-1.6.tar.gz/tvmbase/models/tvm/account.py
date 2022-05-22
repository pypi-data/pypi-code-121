from tonclient.types import ParamsOfParse, ParamsOfQueryCollection

from tvmbase.client import Client
from tvmbase.models.data import AccountData
from tvmbase.models.tvm.base import BaseTvm


class Account(BaseTvm):

    def __init__(self, client: Client, address: str, data: AccountData | None):
        super().__init__(client, address)
        self.data = data

    @staticmethod
    def gql_query(address: str) -> ParamsOfQueryCollection:
        return ParamsOfQueryCollection(
            collection='accounts',
            result='boc',
            limit=1,
            filter={'id': {'eq': address}},
        )

    @classmethod
    async def from_boc(cls, client: Client, boc: str, **kwargs) -> 'Account':
        if boc is None:  # account is not exists
            return cls(client, kwargs['id'], data=None)
        parse_params = ParamsOfParse(boc=boc)
        parsed = await client.boc.parse_account(params=parse_params)
        address = parsed.parsed.pop('id')
        data = AccountData(**parsed.parsed, **kwargs)
        return cls(client, address, data)

    @classmethod
    async def from_address(cls, client: Client, address: str) -> 'Account':
        return await cls.from_idx(client, address)

    @property
    def address(self) -> str:
        return self.idx

    @property
    def exists(self) -> bool:
        return self.data is not None

    @property
    def balance(self) -> int:
        return self.data.balance
