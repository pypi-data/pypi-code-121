from collections.abc import (
    Iterable,
    MutableMapping,
)
from typing import Dict


def is_not_none(v):
    return v is not None


def is_essential(v):
    return bool(v)


def filter_none(el, predicate=is_not_none):
    if isinstance(el, Dict):
        return {k: v for k, v in el.items() if predicate(v)}
    elif isinstance(el, Iterable):
        return list(filter(predicate, el))
    else:
        return el


def is_iterable(i):
    try:
        iter(i)
    except TypeError:
        return False
    else:
        return True


def paginator(func, page_size, *args, **kwargs):
    page = 1
    while True:
        data = func(page=page, page_size=page_size, *args, **kwargs)
        yield data
        if data.total < data.page * data.page_size:
            return
        page += 1


def flatten(d, sep='.', prefix=''):
    items = []
    for k, v in d.items():
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, sep=sep, prefix=prefix + k + sep).items())
        else:
            items.append((prefix + k, v))
    return dict(items)


def unflatten(flat_dict, sep='.'):
    unflatted_dict = {}
    for key, value in flat_dict.items():
        parts = key.split(sep)
        d = unflatted_dict
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value
    return unflatted_dict


def merge_dicts(d1, *args):
    merged = dict(d1)
    for d in args:
        merged.update(d)
    return merged


def next_greater_power_of_2(x):
    return 2 ** (x - 1).bit_length()


def smart_merge_dicts(destination, source, list_policy='merge', copy=True):
    if copy:
        destination = dict(destination)

    for key, value in source.items():
        if isinstance(value, dict):
            policy = value.pop('_policy', 'merge')
            if policy == 'override':
                destination[key] = value
            elif policy == 'bypass':
                if key not in destination:
                    destination[key] = value
            elif policy == 'merge':
                destination.setdefault(key, {})
                destination[key] = smart_merge_dicts(destination[key], value, list_policy=list_policy)
        elif isinstance(value, (tuple, list)) and list_policy == 'merge':
            destination.setdefault(key, [])
            if isinstance(destination[key], (tuple, list)):
                destination[key] = [_ for _ in destination[key]]
                destination[key].extend(value)
            else:
                destination[key] = value
        else:
            destination[key] = value

    return destination


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result
