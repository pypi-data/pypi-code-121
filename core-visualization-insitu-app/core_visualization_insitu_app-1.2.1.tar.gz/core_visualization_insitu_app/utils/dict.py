"""Visualization Insitu Dict"""

import json


def get_dict_value(dict_content, key):
    """Recursive method to get the value deep inside json tree

    Args:
        dict_content:  json tree
        key:  key related to the value

    Returns:

    """
    value = 0
    for k, v in list(dict_content.items()):
        if k != key:
            return get_dict_value(v, key)
        else:
            value = v
    return value


def get_dict_path_value_data(dict_content, path):
    """Recursive method to get the value inside json tree from a full path

    Args:
        dict_content:
        path:

    Returns:

    """

    path_list = path.split(".")

    if dict_content:
        if path_list[0] == "dict_content":
            path = path[len("dict_content.") :]
            path_list.pop(0)

        if len(path_list) == 1:
            return dict_content[path]
        else:
            substr_length = len(path_list[0]) + 1  # +1 to substring the point
            return get_dict_path_value_data(
                dict_content[path_list[0]], path[substr_length:]
            )

    return "Unknown"


def get_dict_path_value(dict_content, path):
    """Recursive method to get the value inside json tree from a full path

    Args:
        dict_content:
        path:

    Returns:

    """
    path_list = path.split(".")

    if dict_content:
        if path_list[0] == "dict_content":
            return get_dict_path_value(dict_content, path[(len(path_list[0]) + 1) :])

        if len(path_list) == 1:
            return dict_content[path]
        else:
            substr_length = len(path_list[0]) + 1  # +1 to substring the point
            return get_dict_path_value(dict_content[path_list[0]], path[substr_length:])

    return ""


def get_list_inside_dict(dict_path, dict_content):
    """return a list of a single dict.
    This method goes throughout the dict 'dict_content' given in argument according to the path 'dict_path'

    Args:
        dict_path: key1.key2.key3...keyx
        dict_content: {key1: {key2: {key3:...{keyx:{dict_content_to_return}}

    Returns:

    """
    if not isinstance(dict_path, list):
        dict_path = dict_path.split(".")

    if dict_path[0] == "dict_content":
        dict_path.pop(0)

    if isinstance(dict_content, dict):
        if dict_path[-1] not in json.dumps(dict_content):
            return None
        if len(dict_path) == 1:
            return [dict_content]
        else:
            return get_list_inside_dict(dict_path[1:], dict_content[dict_path[0]])
    else:
        if len(dict_path) != 1:
            return get_dicts_inside_list_of_dict(dict_path, dict_content)
        return dict_content


def get_dicts_inside_list_of_dict(list_path, list_of_dict):
    """

    Args:
        list_path:  [a,b,c]
        list_of_dict:  [{a:{b:{c:value1},{a:{b:{c:value2}, ..]

    Returns: [{c:value1}, {c:value2},..]

    """
    while len(list_path) > 1:
        for dict_to_parse in list_of_dict:
            list_of_dict[list_of_dict.index(dict_to_parse)] = dict_to_parse[
                list_path[0]
            ]
        list_path = list_path[1:]

    if len(list_path) == 1:
        return list_of_dict
