__all__ = ('UploadFilePoint', 'UserFileObjectPoint')

from django.core.validators import RegexValidator

from expressmoney.api import *

SERVICE = 'storage'


class UploadFileResponseContract(Contract):
    alphanumeric = RegexValidator(r'^[0-9a-zA-Z_]*$', 'Only alphanumeric characters are allowed.')
    name = serializers.CharField(max_length=64, validators=(alphanumeric,))


class UserFileReadContract(UploadFileResponseContract):
    id = serializers.IntegerField(min_value=1)
    public_url = serializers.URLField(allow_null=True)
    file = serializers.URLField()


class UserFileID(ID):
    _service = SERVICE
    _app = 'storage'
    _view_set = 'user_file'


class UploadFileID(ID):
    _service = SERVICE
    _app = 'storage'
    _view_set = 'upload_file/'


class UserFileObjectPoint(RetrievePointMixin, ContractObjectPoint):
    _point_id = UserFileID()
    _read_contract = UserFileReadContract


class UploadFilePoint(UploadFilePointMixin, ResponseMixin, ContractPoint):
    _point_id = UploadFileID()
    _response_contract = UploadFileResponseContract
    _read_contract = None
