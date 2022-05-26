from functools import reduce

ts_type_mapping = {
    'string': [
        'text',
        'string',
        'select',
        'checkbox',
        'readio'
    ],
    'number': [
        'number',
        'integer'
    ],
    'ObjectId': [
        'module',
        'objectid'
    ],
    'boolean': 'boolean',
    'Date': 'datetime',
    'any': 'object',
}

def extract_entity(field:dict) -> str:
    def extract_query(value:dict) -> dict:
        return value.get('__query', None) \
            if type(value) is dict else None

    is_array = field.get('array', False)

    if module := field.get('module'):
        return module, is_array

    if values := field.get('values'):
        if query := extract_query(
            values
            if not isinstance(field['values'], list)
            else field['values'][0]
        ):
            return (
                query['module'],
                is_array or isinstance(field['values'], list)
            )

def extract_entities(fields:dict) -> str:
    for k, v in fields.items():
        _tuple = extract_entity(v)
        if _tuple:
            yield _tuple

def convert_type(name:str) -> dict:
    return next((
        k
        for k, v in ts_type_mapping.items()
        if name in v
    ), None)

def map_fields(fields:dict) -> dict:
    def reducer(a:dict, item:tuple) -> dict:
        k, v = item
        field_type = v.get('type', 'text')

        _tuple = extract_entity(v)
        if _tuple:
            module, is_array = _tuple
            return a | { k: '{}Document{}'.format(
                module[0].upper() + module[1:],
                '[]' if is_array else ''
            ) }

        return a | { k: convert_type(field_type) }
    return reduce(reducer, fields.items(), {})

def make_ts_typehints(obj:dict) -> str:
    def reducer(a:str, item:tuple) -> list:
        k, v = item
        return a + ["  {}: {}".format(k, v)]
    return "\n".join(reduce(reducer, obj.items(), []))

