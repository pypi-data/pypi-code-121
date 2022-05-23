__all__ = ('UnderwritingTaskPoint',)

from expressmoney.api import *

SERVICE = 'sync'


class UnderwritingTaskReadContract(Contract):
    created = serializers.DateTimeField(allow_null=True)
    profile = serializers.IntegerField(min_value=1)
    is_success = serializers.BooleanField()


class UnderwritingTaskID(ID):
    _service = SERVICE
    _app = 'underwriting'
    _view_set = 'underwriting_task'


class UnderwritingTaskPoint(ListPointMixin, ContractPoint):
    _point_id = UnderwritingTaskID()
    _read_contract = UnderwritingTaskReadContract
    _sort_by = 'created'
    _cache_enabled = False
