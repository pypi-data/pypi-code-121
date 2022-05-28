import inspect
import re
from importlib import (
    import_module,
)

from django.conf import (
    settings,
)
from django.core.exceptions import (
    ImproperlyConfigured,
)
from django.db import (
    models,
)

import m3_gar.base_models
import m3_gar.models


def get_models():
    """
    Возвращает список моделей, относящихся к ГАР
    """
    base_models = tuple(
        obj for name, obj
        in inspect.getmembers(m3_gar.base_models)
        if inspect.isclass(obj) and issubclass(obj, models.Model)
    )

    concrete_models = [
        obj for name, obj
        in inspect.getmembers(m3_gar.models)
        if inspect.isclass(obj) and issubclass(obj, base_models)
    ]

    return concrete_models


def get_table_names_from_models():
    """
    Возвращает названия таблиц
    """

    table_names = [
        re.sub('(?!^)([A-Z]+)', r'_\1', model.__name__).lower()
        for model in get_models()
    ]

    return tuple(table_names)


def get_model_from_table_name(table_name):
    model_name = ''.join(x.title() for x in table_name.split('_'))
    model = getattr(m3_gar.models, model_name, None)
    return model


def get_table_row_filters():
    """
    Перенос функционала из config в функцию
    Достает фильтры для таблиц

    Оригинальное описание:
    см. m3_gar.importer.filters
    указывается список путей к функциям-фильтрам
    фильтры применяются к *каждому* объекту
    один за другим, пока не закончатся,
    либо пока какой-нибудь из них не вернёт None
    если фильтр вернул None, объект не импортируется в БД

    пример:

    GAR_TABLE_ROW_FILTERS = {
        'addrobj': (
            'm3_gar.importer.filters.example_filter_yaroslavl_region',
        ),
        'house': (
            'm3_gar.importer.filters.example_filter_yaroslavl_region',
        ),
    }
    """
    row_filters = getattr(settings, 'GAR_TABLE_ROW_FILTERS', {})
    table_row_filters = {}

    for flt_table, flt_list in row_filters.items():
        if flt_table in get_table_names_from_models():
            for flt_path in flt_list:
                try:
                    module_name, _, func_name = flt_path.rpartition('.')
                    flt_module = import_module(module_name)
                    flt_func = getattr(flt_module, func_name)
                except (ImportError, AttributeError):
                    raise ImproperlyConfigured(
                        'Table row filter module `{0}` does not exists'.format(
                            flt_path))
                else:
                    table_row_filters.setdefault(flt_table, []).append(flt_func)

    return table_row_filters
