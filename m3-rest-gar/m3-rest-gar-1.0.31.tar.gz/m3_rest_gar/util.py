from collections.abc import (
    Iterable,
)
from uuid import (
    UUID,
)

from m3_gar.models.hierarchy import (
    Hierarchy,
)


# Пример административного деления
# 33634065 - д 54
# 210826 - ул Заречная
# 210984 - с Кунгуртуг
# 213492 - р-н Тере-Хольский
# 206101 - Респ Тыва

# Пример муниципального деления
# 33634065 - д 54
# 210826 - ул Заречная
# 210984 - с Кунгуртуг
# 95235279 - с.п. Шынаанский
# 95235278 - м.р-н Тере-Хольский
# 206101 - Респ Тыва


def get_hierarchy_models(hierarchy):
    """Возвращает список моделей иерархии по заданному коду (или нескольким кодам).

    Args:
        hierarchy: Код или список кодов иерархии.
            Примеры: 'adm', 'mun', 'any', ['adm', 'mun']

    Returns:
        Список классов моделей иерархии

    Raises:
        ValueError: неверный код иерархии
    """

    hierarchy_model_map = Hierarchy.get_shortname_map()

    if hierarchy == 'any':
        hierarchy = hierarchy_model_map.keys()
    elif isinstance(hierarchy, str):
        hierarchy = [hierarchy]
    elif isinstance(hierarchy, Iterable):
        pass
    else:
        raise ValueError(f'Invalid hierarchy value: {hierarchy}')

    try:
        hierarchy_models = [hierarchy_model_map[h] for h in hierarchy]
    except KeyError as e:
        raise ValueError(f'Invalid hierarchy value: {e}')

    return hierarchy_models


def is_objectguid(value):
    try:
        UUID(value)
    except ValueError:
        result = False
    else:
        result = True

    return result
