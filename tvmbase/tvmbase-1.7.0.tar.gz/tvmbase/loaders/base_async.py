from abc import ABC, abstractmethod

from loguru import logger

from tvmbase.client import Client
from tvmbase.loaders.batch import BatchLoader
from tvmbase.models.boc_type import BocType
from tvmbase.models.tvm.account import Account
from tvmbase.models.tvm.base import BaseTvm
from tvmbase.models.tvm.message import Message
from tvmbase.models.tvm.transaction import Transaction


class BaseAsyncLoader(ABC):

    def __init__(self, client: Client, parallels: int, batch_size: int):
        self.parallels = parallels
        self.batch_size = batch_size

        self.messages: dict[str, Message] = dict()
        self.transactions: dict[str, Transaction] = dict()
        self.accounts: dict[str, Account] = dict()

        self.batch_loader = BatchLoader(client)
        logger.success(f'Created loader, {parallels=} and {batch_size=}')

    @abstractmethod
    def add_initial(self, message_idx: str):
        pass

    @abstractmethod
    def _queued_task(self, idx: str, boc_type: BocType):
        pass

    async def load(self, with_accounts: bool = True):
        await self.load_messages()
        await self.load_transactions()
        if with_accounts:
            await self.load_accounts()

    @abstractmethod
    async def load_messages(self):
        pass

    @abstractmethod
    async def load_transactions(self):
        pass

    async def load_accounts(self):
        logger.info(f'Loading accounts...')
        addresses = set()
        for message in self.messages.values():
            addresses.add(message.data.src)
            addresses.add(message.data.dst)
        for transaction in self.transactions.values():
            addresses.add(transaction.data.account_addr)
        addresses.discard('')  # for external messages src account is ''
        for address in addresses:
            self._queued_task(address, BocType.ACCOUNT)
        await self._run_loader()
        logger.success(f'Loaded accounts')

    @abstractmethod
    async def _run_loader(self):
        pass

    @abstractmethod
    async def _loader_coroutine(self):
        pass

    async def _process_batch(self, batch: list[tuple[str, BocType]]):
        results = await self.batch_loader.load(batch)
        for (idx, boc_type), result in zip(batch, results):
            if boc_type == BocType.MESSAGE and isinstance(result, Message):
                self._process_message(result)
            elif boc_type == BocType.TRANSACTION and isinstance(result, Transaction):
                self._process_transaction(result)
            elif boc_type == BocType.ACCOUNT and isinstance(result, Account):
                self._process_account(result)
            else:
                raise Exception('Unknown result')

    @abstractmethod
    def _process_message(self, message: Message):
        pass

    @abstractmethod
    def _process_transaction(self, transaction: Transaction):
        pass

    @abstractmethod
    def _process_account(self, account: Account):
        pass

    @staticmethod
    @abstractmethod
    def _save(value: BaseTvm, storage: dict[str, BaseTvm]):
        pass
