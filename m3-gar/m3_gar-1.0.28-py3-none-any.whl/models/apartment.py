from m3_gar.base_models import (
    Apartments as BaseApartments,
    ApartmentTypes as BaseApartmentTypes,
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


__all__ = ['Apartments', 'ApartmentTypes']


class ApartmentTypes(BaseApartmentTypes):
    """
    Сведения по типам помещений
    """
    class Meta:
        verbose_name = 'Тип помещения'
        verbose_name_plural = 'Типы помещений'


class Apartments(BaseApartments, RegionCodeModelMixin):
    """
    Сведения по помещениям
    """

    level = 11

    class Meta:
        verbose_name = 'Помещение'
        verbose_name_plural = 'Помещения'


make_fk(Apartments, 'aparttype', to=ApartmentTypes, null=True, blank=True)
make_fk(Apartments, 'opertypeid', to=OperationTypes)
make_fk(Apartments, 'objectid', to=ReestrObjects)

add_params(Apartments, 'm3_gar.ApartmentsParams')
