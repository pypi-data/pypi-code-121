from django.contrib.postgres.indexes import (
    HashIndex,
)

from m3_gar.base_models import (
    Houses as BaseHouses,
    HouseTypes as BaseHouseTypes,
)
from m3_gar.models.op_type import (
    OperationTypes,
)
from m3_gar.models.reestr import (
    ReestrObjects,
)
from m3_gar.models.util import (
    RegionCodeModelMixin,
    add_params,
    make_fk,
)


__all__ = ['Houses', 'HouseTypes', 'AddhouseTypes']


class HouseTypes(BaseHouseTypes):
    """
    Сведения по типам домов
    """
    class Meta:
        verbose_name = 'Тип дома'
        verbose_name_plural = 'Типы домов'


class AddhouseTypes(BaseHouseTypes):
    """
    Сведения по дополнительным типам домов
    """
    class Meta:
        verbose_name = 'Тип дома'
        verbose_name_plural = 'Типы домов'


class Houses(BaseHouses, RegionCodeModelMixin):
    """
    Сведения по номерам домов улиц городов и населенных пунктов
    """

    level = 10

    class Meta:
        verbose_name = 'Номер дома'
        verbose_name_plural = 'Номера домов'

        indexes = (
            HashIndex(
                fields=('objectguid',),
            ),
        )

make_fk(Houses, 'housetype', to=HouseTypes, null=True, blank=True)
make_fk(Houses, 'addtype1', to=AddhouseTypes, null=True, blank=True)
make_fk(Houses, 'addtype2', to=AddhouseTypes, null=True, blank=True)
make_fk(Houses, 'opertypeid', to=OperationTypes)
make_fk(Houses, 'objectid', to=ReestrObjects)

add_params(Houses, 'm3_gar.HousesParams')
