__all__ = ('BankCardPaymentPoint',)

from expressmoney.api import *

SERVICE = 'payments'


class BankCardPaymentCreateContract(Contract):
    amount = serializers.DecimalField(max_digits=16, decimal_places=0, min_value=1)
    withdraw = serializers.BooleanField()
    bank_card = serializers.IntegerField(min_value=1)


class BankCardPaymentResponseContract(BankCardPaymentCreateContract):
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()


class BankCardPaymentReadContract(BankCardPaymentCreateContract):
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()


class BankCardPaymentID(ID):
    _service = SERVICE
    _app = 'payments'
    _view_set = 'bank_card_payment'


class BankCardPaymentPoint(ListPointMixin, ResponseMixin, CreatePointMixin, ContractPoint):
    _point_id = BankCardPaymentID()
    _create_contract = BankCardPaymentCreateContract
    _response_contract = BankCardPaymentResponseContract
    _read_contract = BankCardPaymentReadContract
