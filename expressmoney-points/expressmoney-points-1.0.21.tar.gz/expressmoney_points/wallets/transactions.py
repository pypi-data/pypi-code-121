__all__ = ('TransactionPoint',)

from expressmoney.api import *

SERVICE = 'wallets'
APP = 'transactions'


class TransactionCreateContract(Contract):
    created = serializers.DateField()
    amount = serializers.DecimalField(max_digits=16, decimal_places=0)
    description = serializers.IntegerField(min_value=1)


class TransactionReadContract(TransactionCreateContract):
    wallet = serializers.IntegerField(min_value=1)


class TransactionID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'transaction'


class TransactionPoint(ListPointMixin, CreatePointMixin, ContractPoint):
    _point_id = TransactionID()
    _create_contract = TransactionCreateContract
    _read_contract = TransactionReadContract
    _sort_by = 'priority'
