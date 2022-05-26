from typing import Dict, Any


class ContextData(object):
    def __init__(self, props: Dict[str, Any] = None, **kwargs):
        if props:
            for name, value in props.items():
                super().__setattr__(name, self._wrap(value))
        super().__setattr__('data', kwargs)

    def _wrap(self, value):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v) for v in value])
        else:
            return ContextData(value) if isinstance(value, dict) else value

    def __setattr__(self, key, value):
        super().__setattr__(key, self._wrap(value))
