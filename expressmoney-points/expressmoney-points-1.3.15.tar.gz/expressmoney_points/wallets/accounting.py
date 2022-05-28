__all__ = ('CommissionEntryPoint', 'WalletDepositEntryPoint', 'WalletWithdrawEntryPoint')

from expressmoney.api import *

SERVICE = 'wallets'
APP = 'accounting'


class CommissionEntryReadContract(Contract):
    created = serializers.DateTimeField()
    wallet = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(max_digits=16, decimal_places=0)
    balance = serializers.DecimalField(max_digits=16, decimal_places=0)


class WalletDepositEntryReadContract(CommissionEntryReadContract):
    pass


class WalletWithdrawEntryReadContract(CommissionEntryReadContract):
    pass


class CommissionEntryID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'commission_entry'


class WalletDepositEntryID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'wallet_deposit_entry'


class WalletWithdrawEntryID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'wallet_withdraw_entry'


class CommissionEntryPoint(ListPointMixin, ContractPoint):
    _point_id = CommissionEntryID()
    _read_contract = CommissionEntryReadContract
    _sort_by = 'created'


class WalletDepositEntryPoint(ListPointMixin, ContractPoint):
    _point_id = WalletDepositEntryID()
    _read_contract = WalletDepositEntryReadContract
    _sort_by = 'created'


class WalletWithdrawEntryPoint(ListPointMixin, ContractPoint):
    _point_id = WalletWithdrawEntryID()
    _read_contract = WalletWithdrawEntryReadContract
    _sort_by = 'created'
