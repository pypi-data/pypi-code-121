import json
from os.path import join, dirname
from typing import Dict

from py_dot.core.dicts import merge


def load(json_filename: str, extends_property: str = 'extends', snake_case=False) -> Dict:
    """ json.loads with assign `extends` file as source

    """
    extends_value = json.loads(open(json_filename, 'r').read())
    extends_values = [extends_value]

    while extends_property in extends_value:
        json_filename = join(dirname(json_filename), extends_value[extends_property])
        extends_value = json.loads(open(json_filename, 'r').read())
        extends_values.append(extends_value)

    extends_length = len(extends_values) - 1
    while extends_length > 0:
        previous_index = extends_length - 1
        extends_values[previous_index] = merge(
            extends_values[extends_length],
            extends_values[previous_index],
            False,
            snake_case
        )
        extends_length -= 1

    return extends_values[0]
