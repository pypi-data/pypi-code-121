__all__ = ('ProfileScoringPoint', 'OrderScoringPoint',)

from expressmoney.api import *

SERVICE = 'scoring'


class ProfileScoringCreateContract(Contract):
    pass


class ProfileScoringReadContract(Contract):
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()
    score = serializers.DecimalField(max_digits=3, decimal_places=2)
    credit_dataset = serializers.IntegerField(min_value=1)


class ProfileScoringResponseContract(ProfileScoringReadContract):
    pass


class OrderScoringCreateContract(Contract):
    order_id = serializers.IntegerField(min_value=1)


class OrderScoringResponseContract(Contract):
    id = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField()
    score = serializers.DecimalField(max_digits=3, decimal_places=2)
    order_id = serializers.IntegerField(min_value=1)


class OrderScoringReadContract(OrderScoringResponseContract):
    pass


class ProfileScoringID(ID):
    _service = SERVICE
    _app = 'credit_scoring'
    _view_set = 'profile_scoring'


class OrderScoringID(ID):
    _service = SERVICE
    _app = 'credit_scoring'
    _view_set = 'order_scoring'


class ProfileScoringPoint(ListPointMixin, ResponseMixin, CreatePointMixin, ContractPoint):
    _point_id = ProfileScoringID()
    _create_contract = ProfileScoringCreateContract
    _response_contract = ProfileScoringResponseContract
    _read_contract = ProfileScoringReadContract


class OrderScoringPoint(ListPointMixin, ResponseMixin, CreatePointMixin, ContractPoint):
    _point_id = OrderScoringID()
    _read_contract = OrderScoringReadContract
    _create_contract = OrderScoringCreateContract
    _response_contract = OrderScoringResponseContract
