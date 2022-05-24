__all__ = ('ReferralPoint',)

from django.core.validators import RegexValidator
from expressmoney.api import *

SERVICE = 'partners'


class ReferralCreateContract(Contract):
    partner_code = serializers.CharField(max_length=8,
                                         validators=(RegexValidator(regex='^[A-Z0-9]*$',
                                                                    message='invalid_format',
                                                                    code='invalid_format'
                                                                    ),
                                                     ))


class ReferralReadContract(ReferralCreateContract):
    created = serializers.DateTimeField()
    user_id = serializers.IntegerField(min_value=1)


class ReferralID(ID):
    _service = SERVICE
    _app = 'referrals'
    _view_set = 'referral'


class ReferralPoint(CreatePointMixin, ListPointMixin, ContractPoint):
    _point_id = ReferralID()
    _create_contract = ReferralCreateContract
    _read_contract = ReferralReadContract
