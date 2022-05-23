import json
import re
from types import SimpleNamespace
from typing import Any, AnyStr, Dict, Iterable, List, Match, Optional, Union


class DotDictionary(SimpleNamespace):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        for key, value in data.items():
            if isinstance(value, dict):
                self.__setattr__(key, DotDictionary(value))
            elif isinstance(value, str) or isinstance(value, bytes):
                self.__setattr__(key, value)
            elif isinstance(value, Iterable):
                list_values: List[Any] = []
                for v in value:
                    list_values.append(DotDictionary(v) if isinstance(v, dict) else v)
                self.__setattr__(key, list_values)
            else:
                self.__setattr__(key, value)


class Utils:

    @staticmethod
    def parse_containers_ids(text: str) -> List[str]:
        m: Optional[Match[AnyStr]] = Const.DECODE_RE.match(text)
        containers_ids: List[str] = list()
        if m:
            ids: Optional[str] = m.groupdict().get("values")
            if ids:
                containers_ids = list(filter(None, ids.split('\\n')))
        return containers_ids

    @staticmethod
    def parse_docker_response_helper(text: str) -> \
        Union[List[DotDictionary], DotDictionary, str]:
        try:
            data = json.loads(text)
            if isinstance(data, list):
                if len(data) > 1:
                    result: List[DotDictionary] = list()
                    for d in data:
                        result.append(DotDictionary(d))
                    return result
                else:
                    return DotDictionary(data[0])
            else:
                DotDictionary(data)
        except json.decoder.JSONDecodeError:
            return text


class Const:
    # matches: b'ba34194ed17a8\\n59625d0a834a\\n216a1d3fb5ce\\n817469edd1ff\\n'
    DECODE_RE = re.compile(r'(?i)(b\'(?P<values>.*)\')')
    HOST_IMAGES: Dict[str, str] = {
        "alpine": "./images/alpine/",
        "ubuntu": "./images/ubuntu/",
        "centos": "./images/centos/"
    }
