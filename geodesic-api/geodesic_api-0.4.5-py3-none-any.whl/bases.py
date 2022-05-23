from typing import Any
from functools import wraps


class APIObject(dict):
    """
    Python dictionary with attribute-style setting. This allows us
    to use objects with json.load(s)/dump(s), treat them like a dict
    for most use purposes, but then to simple checks when setting
    attributes.
    """
    # Override this in the inheriting class to specify that only certain items/attributes
    # can be set by the user. Will raise an exception on others.
    # This should be a list of items that are allowed to be set. Every item in this list
    # MUST have a defined property with a setter.
    _limit_setitem = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __setitem__(self, k: str, v: Any) -> None:
        if self._limit_setitem is not None:
            return self._setitem_limited(k, v)

        try:
            if hasattr(self, k):
                try:
                    setattr(self, k, v)
                except AttributeError:
                    self._set_item(k, v)
            elif k in dir(self):
                try:
                    setattr(self, k, v)
                except AttributeError:
                    self._set_item(k, v)
            else:
                self._set_item(k, v)
        except KeyError:
            if k in dir(self):
                try:
                    setattr(self, k, v)
                except AttributeError:
                    self._set_item(k, v)
            else:
                self._set_item(k, v)

    def _setitem_limited(self, k: str, v: Any):
        if k not in self._limit_setitem:
            raise AttributeError(f"'{k}' not allowed to be set on this object")

        try:
            return setattr(self, k, v)
        except AttributeError:
            if k in self._limit_setitem:
                self._set_item(k, v)

    def update(self, *mapping, **kwargs):
        if mapping:
            if len(mapping) > 1:
                raise TypeError(f"update expected at most 1 arguments, got {len(mapping)}")
            other = APIObject(mapping[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    def _set_item(self, k, v):
        super(APIObject, self).__setitem__(k, v)


def reset_attr(f):
    """
    Apply to a property setter method to reset (or set) the property's
    _attr field to None. This enables a property getter to cache the results in
    the _attr variable for expensive computation.
    """
    @wraps(f)
    def wrapped(*args, **kwargs):
        # Call the class method
        res = f(*args, **kwargs)
        # args[0] should be self in a class method
        self = args[0]
        setattr(self, f'_{f.__name__}', None)
        return res

    return wrapped
