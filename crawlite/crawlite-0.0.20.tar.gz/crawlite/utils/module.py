import inspect
from itertools import takewhile
from collections import abc

from .regex import strcompile

from crawlite import settings as default_settings



def find_function(module, regex):
    if not inspect.ismodule(module):
        raise ValueError(f"{module} is Not python module  .py")
    for name, func in inspect.getmembers(module, inspect.isfunction):
        if g := strcompile(regex).search(name):
            yield g.group, func


def module2dict(module):
    return dict(takewhile(lambda i: i[0] != '__builtins__', inspect.getmembers(module)))


# selectable kwargs
def filter_kwargs(callable, *args, **kwargs):
    sig = inspect.signature(callable)
    kw = {}
    for k, v in kwargs.items():
        if k in sig.parameters:
            kw[k] = v
    return callable(*args, **kw)


class FromSettingsMixin:

    def __init__(self,  *args, settings=None, **kwargs):
        super().__init__(*args, **kwargs)
        defaults = module2dict(default_settings)
        if settings:
            if isinstance(settings, abc.Mapping):
                customs = settings
            else:
                customs = module2dict(settings)
            defaults.update(customs)
        for key, value in defaults.items():
            if not hasattr(self, key):
                setattr(self, key, value)


    def apply_settings(self, callable, *args, setting_prefix=None, lower_key=True, **kwargs):
        sig = inspect.signature(callable)
        kw = {**self.__dict__}

        if setting_prefix:
            kw = {
                k.replace(setting_prefix, ''): v for k, v in kw.items()
                if k.startswith(setting_prefix)
            }
        if lower_key:
            kw = {
                k.lower(): v for k,v in kw.items()
            }
        if not setting_prefix:
            kw = {
                k: v for k, v in kw.items()
                if k in sig.parameters
            }
        kwargs = {
            **kwargs,
            **kw,
        }
        return callable(*args, **kwargs)
        



