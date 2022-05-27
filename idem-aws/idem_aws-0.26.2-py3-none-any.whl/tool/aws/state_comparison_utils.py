import json
from typing import Any
from typing import Dict
from typing import List


def are_lists_identical(hub, list1: List, list2: List) -> bool:
    """
    Compare two lists and logs the difference.
    :param list1: first list.
    :param list2: second list.
    :return: true if there is no difference between both lists.
    """
    if (list1 is None or len(list1) == 0) and (list2 is None or len(list2) == 0):
        return True
    if list1 is None or len(list1) == 0 or list2 is None or len(list2) == 0:
        return False

    diff = [i for i in list1 + list2 if i not in list1 or i not in list2]
    result = len(diff) == 0
    if not result:
        hub.log.debug(f"There are {len(diff)} differences:\n{diff[:5]}")
    return result


def standardise_json(hub, value: str or Dict, sort_keys: bool = True):
    # Format json string or dictionary
    if value is None:
        return None

    if isinstance(value, str):
        json_dict = json.loads(value)
    else:
        json_dict = value
    return json.dumps(
        _sorting(json_dict) if sort_keys else json_dict,
        separators=(", ", ": "),
        sort_keys=sort_keys,
    )


def is_json_identical(hub, struct1: str, struct2: str):
    return _sorting(json.loads(struct1)) == _sorting(json.loads(struct2))


def _sorting(obj):
    if isinstance(obj, dict):
        return {k: _sorting(v) for k, v in sorted(obj.items())}
    if isinstance(obj, list):
        if all(isinstance(v, str) for v in obj):
            return sorted(obj)
        else:
            return [_sorting(v) for i, v in sorted(enumerate(obj))]
    return obj


def compare_dicts(hub, source_dict: Dict[str, Any], target_dict: Dict[str, Any]):
    """
    This functions helps in comparing two dicts.
    It compares each key value in both the dicts and return true or false based on the comparison

    Returns:
        {True|False}

    """

    for key, value in source_dict.items():
        if key in target_dict:
            if isinstance(source_dict[key], dict):
                if not compare_dicts(hub, source_dict[key], target_dict[key]):
                    return False
            elif value != target_dict[key]:
                return False
        else:
            return False
    return True
