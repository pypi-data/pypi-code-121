import re
from typing import List
from urllib.parse import urlencode


def to_camel_case(value):
    content: List[str] = value.title().split('_')
    content[0] = content[0].lower()
    return "".join(content)


def to_snake_case(value: str) -> str:
    value = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
    value = re.sub('__([A-Z])', r'_\1', value)
    value = re.sub('([a-z0-9])([A-Z])', r'\1_\2', value)
    return value.lower()


def encode_url_params(d: dict, doseq: bool = True, remove_keys: List[str] = []) -> str:
    remove_keys.append('self')
    filtered = {}
    for k, v in d.items():
        if v is not None and k not in remove_keys:
            if '_' in k:
                filtered[to_camel_case(k)] = v
            else:
                filtered[k] = v

    return urlencode(filtered, doseq)
