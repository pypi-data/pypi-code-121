__all__ = ('FaqPoint', 'GlossaryPoint')

from expressmoney.api import *

SERVICE = 'partners'
APP = 'support'


class FaqReadContract(Contract):
    priority = serializers.IntegerField(min_value=0)
    title = serializers.CharField(max_length=128)
    body = serializers.CharField(max_length=2048)


class GlossaryReadContract(FaqReadContract):
    pass


class FaqID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'faq'


class GlossaryID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'glossary'


class FaqPoint(ListPointMixin, ContractPoint):
    _point_id = FaqID()
    _read_contract = FaqReadContract
    _sort_by = 'priority'


class GlossaryPoint(ListPointMixin, ContractPoint):
    _point_id = GlossaryID()
    _read_contract = GlossaryReadContract
    _sort_by = 'priority'
