__all__ = ('LandingPoint',)

from expressmoney.api import *

SERVICE = 'content'
APP = 'landings'


class LandingTitleReadContract(Contract):
    text = serializers.CharField(max_length=64)


class LandingBodyReadContract(Contract):
    text = serializers.CharField(max_length=512)


class LandingFeatureReadContract(Contract):
    title = serializers.CharField(max_length=64)
    body = serializers.CharField(max_length=512)


class LandingFeaturesSetReadContract(Contract):
    name = serializers.CharField(max_length=32)
    feature_1 = LandingFeatureReadContract()
    feature_2 = LandingFeatureReadContract()
    feature_3 = LandingFeatureReadContract()
    feature_4 = LandingFeatureReadContract()
    feature_5 = LandingFeatureReadContract()


class LandingReadContract(Contract):
    name = serializers.CharField(max_length=32)
    title = LandingTitleReadContract()
    body = LandingBodyReadContract()
    features_set = LandingFeaturesSetReadContract()


class LandingID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'landing'


class LandingPoint(ListPointMixin, ContractPoint):
    _point_id = LandingID()
    _read_contract = LandingReadContract
