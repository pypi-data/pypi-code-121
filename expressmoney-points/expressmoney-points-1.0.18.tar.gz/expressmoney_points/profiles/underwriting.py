__all__ = ('UnderwritingTaskPoint',)
from expressmoney.api import *

SERVICE = 'profiles'


class UnderwritingTaskCreateContract(Contract):
    pass


class UnderwritingTaskID(ID):
    _service = SERVICE
    _app = 'underwriting'
    _view_set = 'underwriting_task'


class UnderwritingTaskPoint(CreatePointMixin, ContractPoint):
    _point_id = UnderwritingTaskID()
    _create_contract = UnderwritingTaskCreateContract
