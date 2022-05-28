from m3_gar.base_models import (
    ChangeHistory as BaseChangeHistory,
    OperationTypes,
)
from m3_gar.models.util import (
    RegionCodeModelMixin,
    make_fk,
)


__all__ = ['ChangeHistory']


class ChangeHistory(BaseChangeHistory, RegionCodeModelMixin):
    """
    Сведения по истории изменений
    """
    class Meta:
        verbose_name = verbose_name_plural = 'История изменений'


make_fk(ChangeHistory, 'opertypeid', to=OperationTypes)
