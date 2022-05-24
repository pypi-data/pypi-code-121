from m3_gar.base_models import (
    NormativeDocs as BaseNormativeDocs,
    NormativeDocsKinds as BaseNormativeDocsKinds,
    NormativeDocsTypes as BaseNormativeDocsTypes,
)
from m3_gar.models.util import (
    RegionCodeModelMixin,
    make_fk,
)


__all__ = ['NormativeDocsKinds', 'NormativeDocsTypes', 'NormativeDocs']


class NormativeDocsKinds(BaseNormativeDocsKinds):
    """
    Сведения по видам нормативных документов
    """
    class Meta:
        verbose_name = 'Вид нормативного документа'
        verbose_name_plural = 'Виды нормативных документов'

    def __str__(self):
        return self.name


class NormativeDocsTypes(BaseNormativeDocsTypes):
    """
    Сведения по типам нормативных документов
    """
    class Meta:
        verbose_name = 'Тип нормативного документа'
        verbose_name_plural = 'Типы нормативных документов'

    def __str__(self):
        return self.name


class NormativeDocs(BaseNormativeDocs, RegionCodeModelMixin):
    """
    Сведения о нормативном документе, являющемся основанием присвоения
    адресному элементу наименования
    """

    # type = tt(to=NormativeDocsTypes, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Нормативный документ'
        verbose_name_plural = 'Нормативные документы'

    def __str__(self):
        return self.name


make_fk(NormativeDocs, 'type', to=NormativeDocsTypes)
make_fk(NormativeDocs, 'kind', to=NormativeDocsKinds)
