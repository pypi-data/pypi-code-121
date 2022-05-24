from django.db import (
    models,
)

from m3_gar.base_models import (
    AdmHierarchy as BaseAdmHierarchy,
    MunHierarchy as BaseMunHierarchy,
)
from m3_gar.models.reestr import (
    ReestrObjects,
)
from m3_gar.models.util import (
    HierarchyMixin,
    RegionCodeModelMixin,
    make_fk,
)
from m3_gar.models.indexes import (
    UpperGinIndex,
)


__all__ = ['AdmHierarchy', 'MunHierarchy']


class Hierarchy(HierarchyMixin):
    """
    Базовый тип сведений по иерархии
    """

    name_with_parents = models.CharField(max_length=500, verbose_name='Полное наименование', blank=True, null=True)

    class Meta:
        abstract = True

    @staticmethod
    def get_shortname_map():
        return {
            subclass.get_shortname(): subclass
            for subclass in Hierarchy.__subclasses__()
        }

    @classmethod
    def get_shortname(cls):
        shortname = ''

        if cls.__name__.endswith(Hierarchy.__name__):
            shortname = cls.__name__[:-len(Hierarchy.__name__)]

        return shortname.lower()


class AdmHierarchy(BaseAdmHierarchy, Hierarchy, RegionCodeModelMixin):
    """
    Сведения по иерархии в административном делении
    """
    class Meta:
        verbose_name = verbose_name_plural = 'Иерархия в административном делении'

        indexes = [
            UpperGinIndex(
                fields=['name_with_parents'],
                name='adm_name_with_parents_gin',
                opclasses=['gin_trgm_ops'],
            ),
        ]


class MunHierarchy(BaseMunHierarchy, Hierarchy, RegionCodeModelMixin):
    """
    Сведения по иерархии в муниципальном делении
    """
    class Meta:
        verbose_name = verbose_name_plural = 'Иерархия в муниципальном делении'

        indexes = [
            UpperGinIndex(
                fields=['name_with_parents'],
                name='mun_name_with_parents_gin',
                opclasses=['gin_trgm_ops'],
            ),
        ]

    def get_allowed_oktmo(self):
        return [
            self.oktmo[:2].ljust(8, '0'),  # Федеральный уровень
            self.oktmo[:5].ljust(8, '0'),  # Муниципальный уровень
            self.oktmo[:8],  # Уровень населенного пункта
        ]

    def get_ancestors(self, include_self=False):
        ancestors = super().get_ancestors(include_self)

        already_used_ids = []
        unique_ancestors = []

        for each in ancestors:
            if each.id not in already_used_ids:
                already_used_ids.append(each.id)
                unique_ancestors.append(each)

        if len(ancestors) == len(unique_ancestors):
            result = ancestors
        else:
            # Если попали в эту ветку, значит в иерархии есть несколько
            # родителей с одним id, но разным ОКТМО
            allowed_oktmo = self.get_allowed_oktmo()
            result = []
            for ancestor in unique_ancestors:
                if ancestor.oktmo in allowed_oktmo:
                    result.append(ancestor)

        return result


make_fk(AdmHierarchy, 'objectid', to=ReestrObjects)
make_fk(MunHierarchy, 'objectid', to=ReestrObjects)

make_fk(AdmHierarchy, 'parentobjid', to=ReestrObjects)
make_fk(MunHierarchy, 'parentobjid', to=ReestrObjects)
