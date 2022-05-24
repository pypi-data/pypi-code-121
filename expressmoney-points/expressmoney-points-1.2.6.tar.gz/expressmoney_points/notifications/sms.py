__all__ = ('SmsPoint',)

from expressmoney.api import *

SERVICE = 'notifications'


class SmsCreateContract(Contract):
    message = serializers.CharField(min_length=1, max_length=60)


class SmsID(ID):
    _service = SERVICE
    _app = 'sms'
    _view_set = 'sms'


class SmsPoint(CreatePointMixin, ContractPoint):
    _point_id = SmsID()
    _create_contract = SmsCreateContract
