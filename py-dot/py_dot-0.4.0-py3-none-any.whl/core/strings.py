from typing import Dict
import base64
import re

_KEBAB_FLAG = r'(?:_([a-zA-Z])|([A-Z]))'


def to_snake(value: str) -> str:
    """ String casing to snake_case

    - camelCase: camel_case
    - space case: space_case
    - kebab-case: kebab_case

    :param value: Target Value
    :return:
    """
    words = re.findall(r'([A-Z]?[^_\-\sA-Z]+)', value)
    return '_'.join(map(lambda x: x.lower(), words))


def to_kebab(value: str) -> str:
    """ String casing to kebab-case

    """
    return (value[0] + re.sub(_KEBAB_FLAG, r'-\1\2', value[1:])).lower()


def to_spinal(value: str) -> str:
    """ String casing to spinal-case
    """
    return to_kebab(value)


def to_base64(value: str):
    encoded_value = base64.urlsafe_b64encode(value.encode('utf-8'))
    return str(encoded_value, 'utf-8')


def from_base64(value: str):
    decoded_value = base64.urlsafe_b64decode(value)
    return str(decoded_value, 'utf-8')


def ng_interpolated_template(template: str, variables: Dict[str, any]) -> str:
    """ Set Template Variables to Template String
    with Angular Style Text Interpolation(`{{`, `}}`)

    >>> ng_interpolated_template('{{variable_name}}', {'variable_name': 1})

    :param template: template string
    :param variables: template values

    """
    current = -1
    end = len(template) - 1
    result = ''
    stack = ''
    opened = 0
    closed = 0
    while current < end:
        current += 1

        char = template[current]

        if char == '{':
            opened = opened + 1
            continue

        if char == '}':
            closed = closed + 1
            if opened == 2 and closed == 2:
                opened = 0
                closed = 0

                name = stack.strip()
                stack = ''

                if name in variables:
                    result += str(variables[name])
                else:
                    result += '{{' + name + '}}'

            continue

        if opened:
            stack += char
            continue

        result += char

    if stack:
        result += stack

    return result
