from copy import (
    deepcopy,
)

from django.db import (
    connections,
    models,
)

from m3_gar import (
    config,
)


class ConstraintsEditor:

    def __init__(self, *, enable, fk, unique, index):
        self.enable = enable
        self.fk = fk
        self.unique = unique
        self.index = index

    def get_simple_field(self, field):
        """
        Возвращает упрощённую копию переданного поля с отключенными индексами,
        уникальными ограничениями и проверками внешних ключей
        """

        new_field = deepcopy(field)

        if self.unique:
            new_field._unique = False

        if self.index:
            new_field.db_index = False

        if self.fk and any((
            isinstance(field, models.ForeignKey),
            isinstance(field, models.ManyToManyField) and field.remote_field.through is None,
        )):
            new_field.db_constraint = False

        return new_field

    def get_simple_fields(self, model):
        """
        Возвращает пары (поле, упрощённая копия поля) для всех собственных полей модели
        """

        fields = model._meta.get_fields(include_parents=False, include_hidden=False)

        for field in fields:
            if field.concrete:
                yield field, self.get_simple_field(field)

    @staticmethod
    def alter_field(model, field_from, field_to):
        """
        Производит преобразование поля field_from на field_to модели model
        в БД для записей ГАР

        Args:
            model: модель
            field_from: исходное поле
            field_to: новое поле

        Returns:
            список выполненных sql-запросов

        """
        con = connections[config.DATABASE_ALIAS]
        ed = con.schema_editor(collect_sql=True)

        ed.alter_field(model, field_from, field_to)

        return ed.collected_sql

    def change_model_constraints(self, model):
        """
        Удаляет ограничения и индексы модели
        """
        for field, simple_field in self.get_simple_fields(model=model):

            field_from, field_to = field, simple_field

            if self.enable:
                field_from, field_to = field_to, field_from

            yield self.alter_field(model=model, field_from=field_from, field_to=field_to)
