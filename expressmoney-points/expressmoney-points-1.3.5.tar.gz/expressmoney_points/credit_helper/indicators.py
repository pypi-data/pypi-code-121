__all__ = ('IndicatorPoint', 'IndicatorFillingTaskPoint')

from expressmoney.api import *

SERVICE = 'credit_helper'
APP = 'indicators'


class IndicatorFillingTaskCreateContract(Contract):
    pass


class IndicatorReadContract(Contract):
    BAD = 'BAD'
    GOOD = 'GOOD'
    RATE_CHOICES = (
        (BAD, BAD),
        (GOOD, GOOD),
    )
    created = serializers.DateTimeField(auto_now_add=True)
    value = serializers.IntegerField(min_value=0)
    rate = serializers.CharField(max_length=8, choices=RATE_CHOICES)
    recommendation = serializers.CharField(max_length=1024)


class IndicatorFillingTaskID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'indicator_filling_task'


class IndicatorID(ID):
    _service = SERVICE
    _app = APP
    _view_set = 'indicator'


class IndicatorFillingTaskPoint(CreatePointMixin, ContractPoint):
    _point_id = IndicatorFillingTaskID()
    _create_contract = IndicatorFillingTaskCreateContract


class IndicatorPoint(ListPointMixin, ContractPoint):
    _point_id = IndicatorID()
    _read_contract = IndicatorReadContract
    _sort_by = 'created'
