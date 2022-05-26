import json
import pathlib
from functools import reduce
from string import Template
from savitrigen.path import PathlibWrapper

def TreeClass(layer:str, scope:str=None):
    def decorator(cls):
        cls.layer = layer
        cls.scope = scope
        class TreeClass(cls, Tree):
            pass
        return TreeClass
    return decorator

class Tree(object):
    path = None
    parent_dir: str

    def __init__(self):
        self.path = PathlibWrapper()

    def __getattr__(self, attr):
        def wrapped_method(*args, **kwargs):
            if hasattr(self.path, attr):
                if not self.path.parent_dir:
                    self.path.parent_dir = 'packages/{}{}'.format(
                        f'{self.scope}-' if self.scope else '',
                        self.layer
                    )

                path = '{}/{}'.format(self.path.parent_dir, args[0]) \
                    if not isinstance(args[0], pathlib.Path) \
                    else args[0]

                return getattr(self.path, attr)(path, *args[1:], **kwargs)
        return wrapped_method

    @staticmethod
    def _multiline_replace(subjects:list, template:Template, func) -> str:
        def reducer(a:str, item) -> str:
            result = func(item)
            return a + [template.substitute(**result)]

        return "\n".join(reduce(reducer, subjects, []))\

    @staticmethod
    def _json_dumps(what:object) -> str:
        return json.dumps(what, indent=2, ensure_ascii=False)

    @staticmethod
    def _capitalize(string:str) -> str:
        return string[0].upper() + string[1:]

    @staticmethod
    def _pascal_case(string:str) -> str:
        return string[0].upper() + string[1:]

    @staticmethod
    def _camel_case(string:str) -> str:
        return string[0].lower() + string[1:]
