from django.contrib.postgres.indexes import (
    HashIndex,
)

from m3_gar.base_models import (
    Param as BaseParam,
    ParamTypes as BaseParamTypes,
)
from m3_gar.models.util import (
    RegionCodeModelMixin,
    make_fk,
)


__all__ = [
    'ParamTypes',
    'AddrObjParams',
    'ApartmentsParams',
    'CarplacesParams',
    'HousesParams',
    'RoomsParams',
    'SteadsParams',
]


class ParamTypes(BaseParamTypes):
    """
    Сведения по типу параметра
    """
    class Meta:
        verbose_name = 'Тип параметра'
        verbose_name_plural = 'Типы параметров'


class Param(BaseParam, RegionCodeModelMixin):
    """
    Сведения о классификаторе параметров адресообразующих элементов и объектов недвижимости
    """
    class Meta:
        abstract = True
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'

        indexes = (
            HashIndex(
                fields=('objectid',),
            ),
        )


make_fk(Param, 'typeid', to=ParamTypes)


class AddrObjParams(Param):
    pass


class ApartmentsParams(Param):
    pass


class CarplacesParams(Param):
    pass


class HousesParams(Param):
    pass


class RoomsParams(Param):
    pass


class SteadsParams(Param):
    pass
