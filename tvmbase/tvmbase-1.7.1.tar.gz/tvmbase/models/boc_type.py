from enum import Enum

from tvmbase.models.tvm.account import Account
from tvmbase.models.tvm.message import Message
from tvmbase.models.tvm.transaction import Transaction


class BocType(Enum):
    ACCOUNT = Account
    MESSAGE = Message
    TRANSACTION = Transaction

    def __str__(self) -> str:
        return self.name

    __repr__ = __str__
