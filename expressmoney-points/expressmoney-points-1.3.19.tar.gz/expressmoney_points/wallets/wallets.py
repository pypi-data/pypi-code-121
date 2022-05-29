__all__ = ('WalletPoint', 'WalletObjectPoint')

from expressmoney.api import *

SERVICE = 'wallets'
APP = 'wallets'


class WalletCreateContract(Contract):
    RUB = 'RUB'
    USD = 'USD'
    CURRENCY_CODE_CHOICES = (
        (RUB, RUB),
        (USD, USD),
    )
    currency_code = serializers.ChoiceField(choices=CURRENCY_CODE_CHOICES)


class WalletReadContract(WalletCreateContract):
    id = serializers.IntegerField(min_value=1)
    user_id = serializers.IntegerField(min_value=1)
    balance = serializers.DecimalField(max_digits=16, decimal_places=0)


class WalletID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'wallet'


class WalletPoint(ListPointMixin, CreatePointMixin, ContractPoint):
    _point_id = WalletID()
    _create_contract = WalletCreateContract
    _read_contract = WalletReadContract


class WalletObjectPoint(RetrievePointMixin, ContractObjectPoint):
    _point_id = WalletID()
    _read_contract = WalletReadContract
