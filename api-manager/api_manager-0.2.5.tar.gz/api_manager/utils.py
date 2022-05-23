import json
from typing import Union


def prettify_json(payload: Union[dict, list, None], line_break='\n') -> str:
    """
    :param line_break:
    :param payload:
    :return:
    """
    if payload is None:
        return 'null'
    return line_break + json.dumps(payload, sort_keys=True, indent=4)
