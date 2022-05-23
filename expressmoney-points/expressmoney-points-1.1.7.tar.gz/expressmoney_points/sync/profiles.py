__all__ = ('ProfilePoint', 'UserProfilePoint')

from expressmoney.api import *

SERVICE = 'sync'


class ProfileReadContract(Contract):
    user_profile = serializers.IntegerField(min_value=1)
    created = serializers.DateTimeField(allow_null=True)


class UserProfileReadContract(Contract):
    created = serializers.DateTimeField()
    user_id = serializers.IntegerField(min_value=1)
    department = serializers.IntegerField(min_value=1)
    ip = serializers.IPAddressField()
    http_referer = serializers.URLField()
    country = serializers.CharField(max_length=2)


class ProfileID(ID):
    _service = SERVICE
    _app = 'profiles'
    _view_set = 'profile'


class UserProfileID(ID):
    _service = SERVICE
    _app = 'profiles'
    _view_set = 'user_profile'


class ProfilePoint(ListPointMixin, ContractPoint):
    _point_id = ProfileID()
    _read_contract = ProfileReadContract
    _sort_by = 'created'
    _cache_enabled = False


class UserProfilePoint(ListPointMixin, ContractPoint):
    _point_id = UserProfileID()
    _read_contract = UserProfileReadContract
    _sort_by = 'created'
    _cache_enabled = False
