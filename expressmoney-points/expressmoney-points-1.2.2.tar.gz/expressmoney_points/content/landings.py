__all__ = ('LandingPoint',)

from expressmoney.api import *

SERVICE = 'content'
APP = 'landings'


class LandingReadContract(Contract):
    pass


class LandingID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'landing'


class LandingPoint(ListPointMixin, ContractPoint):
    _point_id = LandingID()
    _read_contract = LandingReadContract
