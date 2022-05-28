__all__ = ('OperationDescriptionPoint',)

from expressmoney.api import *

SERVICE = 'wallets'
APP = 'operations'


class OperationDescriptionReadContract(Contract):
    TO_WALLET_FROM_BANK_CARD = 'TO_WALLET_FROM_BANK_CARD'
    FROM_WALLTET_TO_BANK_CARD = 'TO_BANK_CARD'
    FROM_WALLTET_TO_WALLET = 'FROM_WALLTET_TO_WALLET'
    TO_WALLTET_FROM_WALLET = 'TO_WALLTET_FROM_WALLET'
    NAME_CHOICES = (
        (TO_WALLET_FROM_BANK_CARD, TO_WALLET_FROM_BANK_CARD),
        (FROM_WALLTET_TO_BANK_CARD, FROM_WALLTET_TO_BANK_CARD),
        (FROM_WALLTET_TO_WALLET, FROM_WALLTET_TO_WALLET),
        (TO_WALLTET_FROM_WALLET, TO_WALLTET_FROM_WALLET),
    )
    RUB = 'RUB'
    USD = 'USD'
    CURRENCY_CODE_CHOICES = (
        (RUB, RUB),
        (USD, USD),
    )
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    name = serializers.ChoiceField(choices=NAME_CHOICES)
    currency_code = serializers.ChoiceField(choices=CURRENCY_CODE_CHOICES)
    commission_rate = serializers.DecimalField(max_digits=2, decimal_places=2)
    commission_min = serializers.DecimalField(max_digits=16, decimal_places=0)
    amount_min = serializers.DecimalField(max_digits=16, decimal_places=0)
    amount_max = serializers.DecimalField(max_digits=16, decimal_places=0)
    wallet_limit = serializers.DecimalField(max_digits=16, decimal_places=0)


class OperationDescriptionID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'operation_description'


class OperationDescriptionPoint(ListPointMixin, ContractPoint):
    _point_id = OperationDescriptionID()
    _read_contract = OperationDescriptionReadContract
