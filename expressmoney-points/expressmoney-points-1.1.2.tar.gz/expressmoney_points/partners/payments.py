__all__ = ('PartnerPaymentPoint',)

from expressmoney.api import *

SERVICE = 'partners'
APP = 'payments'


class PartnerPaymentCreateContract(Contract):
    amount = serializers.DecimalField(max_digits=16, decimal_places=0)


class PartnerPaymentReadContract(Contract):
    created = serializers.DateTimeField()
    partner = serializers.IntegerField(min_value=1)
    description = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(max_digits=16, decimal_places=0)
    balance = serializers.DecimalField(max_digits=16, decimal_places=0)


class PartnerPaymentID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'partner_payment'


class PartnerPaymentPoint(ListPointMixin, CreatePointMixin, ContractPoint):
    _point_id = PartnerPaymentID()
    _create_contract = PartnerPaymentCreateContract
    _read_contract = PartnerPaymentReadContract
    _sort_by = 'created'
