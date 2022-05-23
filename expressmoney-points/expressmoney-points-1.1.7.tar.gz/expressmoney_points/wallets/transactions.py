__all__ = ('WalletTransactionPoint',)

from expressmoney.api import *

SERVICE = 'wallets'
APP = 'transactions'


class WalletTransactionCreateContract(Contract):
    amount = serializers.DecimalField(max_digits=16, decimal_places=0)
    description = serializers.IntegerField(min_value=1)


class WalletTransactionReadContract(WalletTransactionCreateContract):
    created = serializers.DateField()
    wallet = serializers.IntegerField(min_value=1)


class WalletTransactionID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'wallet_transaction'


class WalletTransactionPoint(ListPointMixin, CreatePointMixin, ContractPoint):
    _point_id = WalletTransactionID()
    _create_contract = WalletTransactionCreateContract
    _read_contract = WalletTransactionReadContract
    _sort_by = 'priority'
