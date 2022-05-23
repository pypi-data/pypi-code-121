from typing import Dict, Any

from py_dot.core.strings import to_snake


def merge(
        target: Dict,
        source: Dict,
        list_merge=True,
        snake_case=False
) -> Dict:
    """ Merge Two Dict to Single Dict

    >>> merge({'a': [1], 'b': True}, {'a':[2], 'c': False})
    ... {
    ... 'a': [1, 2]
    ... 'b': True,
    ... 'c': False
    ... }
    """
    result = {**target}

    if snake_case:
        for name in source:
            snake_name = to_snake(name)
            source_value = source[name]
            if name not in result:
                result[snake_name] = source_value
                continue

            target_value = result[name]

            if isinstance(source_value, dict) and isinstance(target_value, dict):
                result[snake_name] = merge(target_value, source_value, list_merge, snake_case)
                continue

            if list_merge and isinstance(source_value, list) and isinstance(target_value, list):
                result[snake_name] = [*target_value, *source_value]
                continue

            result[name] = source_value
    else:
        for name in source:
            source_value = source[name]
            if name not in result:
                result[name] = source_value
                continue

            target_value = result[name]

            if isinstance(source_value, dict) and isinstance(target_value, dict):
                result[name] = merge(target_value, source_value, list_merge)
                continue

            if list_merge and isinstance(source_value, list) and isinstance(target_value, list):
                result[name] = [*target_value, *source_value]
                continue

            result[name] = source_value

    return result


def to_snake_key(values: Dict[str, Any]) -> Dict:
    snake_values = {}

    for name in values:
        snake_values[to_snake(name)] = values[name]

    return snake_values
