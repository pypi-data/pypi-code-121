from m3_gar.base_models import (
    Steads as BaseSteads,
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


__all__ = ['Steads']


class Steads(BaseSteads, RegionCodeModelMixin):
    """
    Сведения по земельным участкам
    """

    level = 9

    class Meta:
        verbose_name = 'Земельный участок'
        verbose_name_plural = 'Земельные участки'


make_fk(Steads, 'opertypeid', to=OperationTypes)
make_fk(Steads, 'objectid', to=ReestrObjects)

add_params(Steads, 'm3_gar.SteadsParams')
