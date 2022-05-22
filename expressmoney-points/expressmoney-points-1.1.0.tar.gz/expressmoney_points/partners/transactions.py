__all__ = ('PartnerTransactionPoint',)

from expressmoney.api import *

SERVICE = 'partners'
APP = 'transactions'


class PartnerTransactionCreateContract(Contract):
    amount = serializers.DecimalField(max_digits=16, decimal_places=0)


class PartnerTransactionReadContract(Contract):
    created = serializers.DateTimeField()
    partner = serializers.IntegerField(min_value=1)
    description = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(max_digits=16, decimal_places=0)
    balance = serializers.DecimalField(max_digits=16, decimal_places=0)


class PartnerTransactionID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'partner_transaction'


class PartnerTransactionPoint(ListPointMixin, CreatePointMixin, ContractPoint):
    _point_id = PartnerTransactionID()
    _create_contract = PartnerTransactionCreateContract
    _read_contract = PartnerTransactionReadContract
    _sort_by = 'created'
