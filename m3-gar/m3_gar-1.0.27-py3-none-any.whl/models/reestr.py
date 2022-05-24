from django.contrib.postgres.indexes import (
    HashIndex,
)

from m3_gar.base_models import (
    ObjectLevels as BaseObjectLevels,
    ReestrObjects as BaseReestrObjects,
)
from m3_gar.models.util import (
    RegionCodeModelMixin,
    make_fk,
)


__all__ = ['ObjectLevels', 'ReestrObjects']


class ObjectLevels(BaseObjectLevels):
    """
    Сведения по уровням адресных объектов
    """
    class Meta:
        verbose_name = 'Уровень адресного объекта'
        verbose_name_plural = 'Уровни адресных объектов'

    @staticmethod
    def get_model_by_level(level):
        from m3_gar.models import (
            AddrObj,
            Apartments,
            Carplaces,
            Houses,
            Rooms,
            Steads,
        )

        known_models = [
            Apartments,
            Carplaces,
            Houses,
            Rooms,
            Steads,
        ]
        default_model = AddrObj

        level_map = {
            model.level: model
            for model in known_models
        }

        model = level_map.get(level, default_model)

        return model

    @property
    def addr_obj_model(self):
        return self.get_model_by_level(self.level)


class ReestrObjects(BaseReestrObjects, RegionCodeModelMixin):
    """
    Сведения об адресном элементе в части его идентификаторов
    """
    class Meta:
        verbose_name = 'Идентификатор адресного элемента'
        verbose_name_plural = 'Идентификаторы адресных элементов'

        indexes = (
            HashIndex(
                fields=('objectguid',),
            ),
        )

    @property
    def addr_obj_model(self):
        levels_model = self._meta.get_field('levelid').target_field.model
        return levels_model.get_model_by_level(self.levelid_id)

    @property
    def addr_obj_set(self):
        addr_obj_model = self.addr_obj_model

        class AddrObjManager(addr_obj_model._default_manager.__class__):
            def get_queryset(manager):
                return super().get_queryset().filter(objectid=self.objectid)

        manager = AddrObjManager()
        manager.model = addr_obj_model

        return manager


make_fk(ReestrObjects, 'levelid', to=ObjectLevels)
