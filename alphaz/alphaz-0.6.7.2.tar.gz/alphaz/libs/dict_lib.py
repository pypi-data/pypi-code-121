def sort_dict(x, value=False, reverse=False):
    sorted_x = {
        x: y
        for x, y in sorted(
            x.items(), key=lambda kv: kv[1 if value else 0], reverse=reverse
        )
    }
    return sorted_x


def get_nested_dict_from_list(in_list) -> dict:
    """Convert list ['a','b','c'] to a nested dict {'a':{'b':{'c':{}}}}

    Args:
        in_list ([list]): list to convert

    Returns:
        [dict]: list converted to nested dict
    """
    out = {}
    for key in reversed(in_list):
        out = {key: out}
    return out


def get_nested(data, *args):
    if args and data:
        element = args[0]
        if element:
            value = data.get(element)
            return value if len(args) == 1 else get_nested(value, *args[1:])


def merge_dict(d1: dict, d2: dict) -> dict:
    """update first dict with second recursively

    Args:
        d1 (dict): [description]
        d2 (dict): [description]

    Returns:
        dict: [description]
    """
    if d1 is None or type(d1) != dict:
        return d1
    for k, v in d1.items():
        if k in d2 and type(d2) == dict:
            d2[k] = merge_dict(v, d2[k])
    d1.update(d2)
    return d1
