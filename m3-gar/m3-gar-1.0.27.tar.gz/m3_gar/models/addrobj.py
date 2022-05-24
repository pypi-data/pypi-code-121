from django.contrib.postgres.indexes import (
    BTreeIndex,
    HashIndex,
)
from django.utils.functional import (
    cached_property,
)

from m3_gar.base_models import (
    AddrObj as BaseAddrObj,
    AddrObjDivision as BaseAddrObjDivision,
    AddrObjTypes as BaseAddrObjTypes,
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


__all__ = ['AddrObj', 'AddrObjDivision', 'AddrObjTypes']


class AddrObjDivision(BaseAddrObjDivision, RegionCodeModelMixin):
    """
    Сведения по операциям переподчинения
    """
    class Meta:
        verbose_name = 'Операция переподчинения'
        verbose_name_plural = 'Операции переподчинения'


class AddrObjTypes(BaseAddrObjTypes):
    """
    Сведения по типам адресных объектов
    """

    class Meta:
        verbose_name = 'Тип адресного объекта'
        verbose_name_plural = 'Типы адресных объектов'

    @property
    def is_prefix(self):
        """Признак того, является ли тип объекта префиксом."""

        prefix_short_names = {
            'г', 'г.', 'г.ф.з.', 'Респ', 'респ.', 'г.о.', 'г', 'г.', 'дп', 'кп', 'п', 'пгт', 'пгт.', 'рп',
            'автодорога', 'гп', 'д', 'дп.', 'остров', 'с', 'с.',
        }

        return self.shortname in prefix_short_names


class AddrObj(BaseAddrObj, RegionCodeModelMixin):
    """
    Сведения классификатора адресообразующих элементов
    """

    class Meta:
        verbose_name = 'Адресообразующий элемент'
        verbose_name_plural = 'Адресообразующие элементы'

        indexes = (
            HashIndex(
                fields=('objectguid',),
            ),
            BTreeIndex(
                fields=('isactive', 'isactual', 'level'),
            ),
            BTreeIndex(
                fields=('level',),
            ),
        )

    @cached_property
    def addr_obj_type(self):
        """Тип адресного объекта."""

        try:
            result = AddrObjTypes.objects.get(
                shortname=self.typename,
                level=self.level,
            )
        except AddrObjTypes.DoesNotExist:
            result = AddrObjTypes()

        return result

    @property
    def type_full_name(self):
        """Полное наименование типа."""

        return self.addr_obj_type.name

    @property
    def is_prefix_type(self):
        """Признак того, является ли тип объекта префиксом."""

        # 1 - федеральный уровень адресных объектов
        return self.level != '1' or self.addr_obj_type.is_prefix


# На момент описания моделей AddrObjTypes никак не связывается с AddrObj
# Существующее поле AddrObj.typename - текстовое представление (ул, пер, г, и т.п.)
# make_fk(AddrObj, '???', to=AddrObjTypes, null=True, blank=True)

make_fk(AddrObjDivision, 'parentid', to=ReestrObjects, db_constraint=False)
make_fk(AddrObjDivision, 'childid', to=ReestrObjects, db_constraint=False)

make_fk(AddrObj, 'opertypeid', to=OperationTypes)
make_fk(AddrObj, 'objectid', to=ReestrObjects)

add_params(AddrObj, 'm3_gar.AddrObjParams')
