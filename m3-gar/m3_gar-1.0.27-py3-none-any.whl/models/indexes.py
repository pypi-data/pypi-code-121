from django.contrib.postgres.indexes import (
    GinIndex,
)


class UpperGinIndex(GinIndex):
    """
    Доработка стандартного GIN индекса
    """

    def __init__(self, *, fastupdate=True, gin_pending_list_limit=None,
                 opclasses=None, **kwargs):
        kwargs['name'] = kwargs.get('name', 'base_gin_idx')
        super().__init__(
            fastupdate=fastupdate,
            gin_pending_list_limit=gin_pending_list_limit,
            opclasses=opclasses or ['gin_trgm_ops'] * len(kwargs['fields']),
            **kwargs,
        )

    def create_sql(self, model, schema_editor, using='', concurrently=False):
        """
        Позволяет оставить поддержку фильтра icontains,
        следственно - доступен поиск без учёта регистра
        Поэтому делает индекс идентичным этой операции
        """

        statement = super().create_sql(model, schema_editor, using=using)
        quote_name = statement.parts['columns'].quote_name

        statement.parts['columns'].quote_name = (
            lambda column: f'UPPER({quote_name(column)})')

        return statement
