from pydantic import Field

MAP_FIELD_FLAG = 'map_field'


def MapField(*args, **kwargs):
    """
    Has the same functionality as pydantic `Field` but adds a flag to mark the field as map attribute that
    responsible for the decision which map config to load.
    """
    if kwargs.get(MAP_FIELD_FLAG):
        raise ValueError(f'Cannot use "{MAP_FIELD_FLAG}" key inside `MapField()`.')
    return Field(*args, **kwargs, **{MAP_FIELD_FLAG: True})


