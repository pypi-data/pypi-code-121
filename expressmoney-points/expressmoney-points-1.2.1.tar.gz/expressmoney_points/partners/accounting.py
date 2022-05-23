__all__ = ('PartnerPayoutPoint', 'PartnerRevenuePoint', 'PartnerBalancePoint')

from expressmoney.api import *

SERVICE = 'partners'
APP = 'accounting'


class PartnerPayoutCreateContract(Contract):
    amount = serializers.DecimalField(max_digits=16, decimal_places=0)
    bank_card_id = serializers.IntegerField(min_value=1)


class PartnerPayoutReadContract(Contract):
    created = serializers.DateTimeField()
    partner = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(max_digits=16, decimal_places=0)
    balance = serializers.DecimalField(max_digits=16, decimal_places=0)


class PartnerRevenueReadContract(PartnerPayoutReadContract):
    pass


class PartnerBalanceReadContract(PartnerPayoutReadContract):
    pass


class PartnerPayoutID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'partner_payout'


class PartnerRevenueID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'partner_revenue'


class PartnerBalanceID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'partner_balance'


class PartnerPayoutPoint(ListPointMixin, CreatePointMixin, ContractPoint):
    _point_id = PartnerPayoutID()
    _create_contract = PartnerPayoutCreateContract
    _read_contract = PartnerPayoutReadContract
    _sort_by = 'created'


class PartnerRevenuePoint(ListPointMixin, ContractPoint):
    _point_id = PartnerRevenueID()
    _read_contract = PartnerRevenueReadContract
    _sort_by = 'created'


class PartnerBalancePoint(ListPointMixin, ContractPoint):
    _point_id = PartnerBalanceID()
    _read_contract = PartnerBalanceReadContract
    _sort_by = 'created'
