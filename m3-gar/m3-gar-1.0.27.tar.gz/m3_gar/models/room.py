from m3_gar.base_models import (
    Rooms as BaseRooms,
    RoomTypes as BaseRoomTypes,
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


__all__ = ['Rooms', 'RoomTypes']


class RoomTypes(BaseRoomTypes):
    """
    Сведения по типам комнат
    """
    class Meta:
        verbose_name = 'Тип комнаты'
        verbose_name_plural = 'Типы комнат'


class Rooms(BaseRooms, RegionCodeModelMixin):
    """
    Сведения по комнатам
    """

    level = 12

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'


make_fk(Rooms, 'roomtype', to=RoomTypes, null=True, blank=True)
make_fk(Rooms, 'opertypeid', to=OperationTypes)
make_fk(Rooms, 'objectid', to=ReestrObjects)

add_params(Rooms, 'm3_gar.RoomsParams')
