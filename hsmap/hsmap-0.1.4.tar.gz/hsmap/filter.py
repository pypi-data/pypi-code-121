import json
from itertools import product
from typing import Union


def add_pg_pair(li):
    return '(' + ','.join([f"'{i}'" for i in li]) + ')'


def format_value_list(value):
    if not value:
        return [()]
    return [value] if isinstance(value, str) else list(value)


def jsonb_collaborative_filter(jsonb: dict):
    """
    {
        "company_chain_site_list.chain_site": "水泥",
        "company_chain_site_list.second_filed": "下游"
    }
    @param jsonb:
    @return:
    """
    filter_value = list()

    prefix = list(jsonb.keys())[0].split(".")[0]
    keys = [key.split(".")[-1] for key in jsonb.keys()]
    values = list(product(*map(format_value_list, jsonb.values())))

    for item in values:
        if item:
            item_dict = {}
            for i in range(len(item)):
                if item[i]:
                    item_dict.update({keys[i]: item[i]})

            filter_value.append(item_dict)

    if len(filter_value) > 1:
        filter_value = [f"""{prefix} @> '[{json.dumps(v, ensure_ascii=False)}]'""" for v in filter_value]
        return f"({' OR '.join(filter_value)})"
    else:
        return f"""{prefix} @> '[{json.dumps(filter_value[0], ensure_ascii=False)}]'""" if filter_value else None


def filter_constructor(
        key: str,
        value: Union[str, list],
        operter: str = "=",
        effective_judge: bool = False,
) -> str:
    effective_value = ', "is_effective": "1"' if effective_judge else ''

    if len(key.split('.')) == 2:
        operter = "@>"
        key, value_k = key.split('.')
        value = [f'[{{"{value_k}": "{v}"{effective_value}}}]' for v in value] \
            if isinstance(value, list) else f'[{{"{value_k}": "{value}"{effective_value}}}]'

    if operter.upper() == "LIKE":
        value = [f'%{v}%' for v in value] if isinstance(value, list) else f'%{value}%'

    if isinstance(value, list):
        multi_filter_list = [f"{key} {operter} '{v}'" for v in value]
        return f'({" OR ".join(multi_filter_list)})'

    return f"{key} {operter} '{value}'"
