__all__ = ('A48801BalanceAnalyticalPoint', 'A48802BalanceAnalyticalPoint', 'P48809BalanceAnalyticalPoint',
           'P47422BalanceAnalyticalObjectPoint',
           )

from expressmoney.api import *

SERVICE = 'accounting'
APP = 'balances'


class A48801BalanceAnalyticalReadContract(Contract):
    id = serializers.IntegerField(min_value=1)
    updated = serializers.DateTimeField()
    balance = serializers.DecimalField(max_digits=16, decimal_places=0)


class A48802BalanceAnalyticalReadContract(A48801BalanceAnalyticalReadContract):
    pass


class P48809BalanceAnalyticalReadContract(A48801BalanceAnalyticalReadContract):
    pass


class P47422BalanceAnalyticalReadContract(A48801BalanceAnalyticalReadContract):
    pass


class A48801BalanceAnalyticalID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'a48801_balance_analytical'


class A48802BalanceAnalyticalID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'a48802_balance_analytical'


class P48809BalanceAnalyticalID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'p48809_balance_analytical'


class P47422BalanceAnalyticalID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'p47422_balance_analytical'


class A48801BalanceAnalyticalPoint(RetrievePointMixin, ContractObjectPoint):
    _point_id = A48801BalanceAnalyticalID()
    _read_contract = A48801BalanceAnalyticalReadContract


class A48802BalanceAnalyticalPoint(RetrievePointMixin, ContractObjectPoint):
    _point_id = A48802BalanceAnalyticalID()
    _read_contract = A48802BalanceAnalyticalReadContract


class P48809BalanceAnalyticalPoint(RetrievePointMixin, ContractObjectPoint):
    _point_id = P48809BalanceAnalyticalID()
    _read_contract = P48809BalanceAnalyticalReadContract


class P47422BalanceAnalyticalObjectPoint(RetrievePointMixin, ContractObjectPoint):
    _point_id = P47422BalanceAnalyticalID()
    _read_contract = P47422BalanceAnalyticalReadContract
