__all__ = ('PartnerPoint', 'PartnerObjectPoint')

from django.core.validators import RegexValidator
from expressmoney.api import *

SERVICE = 'partners'
APP = 'partners'


class PartnerCreateContract(Contract):
    pass


class PartnerUpdateContract(Contract):
    code = serializers.CharField(max_length=8,
                                 validators=(RegexValidator(regex='^[A-Z0-9]*$',
                                                            message='invalid_format',
                                                            code='invalid_format'
                                                            ),),
                                 )


class PartnerReadContract(PartnerUpdateContract):
    created = serializers.DateTimeField()


class PartnerID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'partner'


class PartnerPoint(CreatePointMixin, ContractPoint):
    _point_id = PartnerID()
    _create_contract = PartnerCreateContract


class PartnerObjectPoint(RetrievePointMixin, UpdatePointMixin, ContractObjectPoint):
    _point_id = PartnerID()
    _read_contract = PartnerReadContract
    _update_contract = PartnerUpdateContract
