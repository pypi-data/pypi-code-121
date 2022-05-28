from m3_gar.base_models import (
    OperationTypes as BaseOperationTypes,
)


__all__ = ['OperationTypes']


class OperationTypes(BaseOperationTypes):
    """
    Сведения по статусу действия
    """
    class Meta:
        verbose_name = 'Статус действия'
        verbose_name_plural = 'Статусы действия'
