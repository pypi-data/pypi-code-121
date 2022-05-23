import datetime
from types import ModuleType
import pytz
import importlib


def is_offset_aware(t: datetime.datetime):
    '''
    Returns True if input is offset aware, False otherwise
    '''
    if t.tzinfo is not None and t.tzinfo.utcoffset(t) is not None:
        return True
    return False


def datetime_to_utc(d: datetime.datetime):
    '''
    Ensures input is localized UTC
    '''

    if is_offset_aware(d):
        return d.astimezone(pytz.UTC)

    return pytz.UTC.localize(d)


class MockImport:
    """
    Use a MockImport when something requires a particular module. On import error,
    set the module instance to this class initialized with the import module name.
    This will raise a readable exception when used instead of a more challenging error.
    """
    def __init__(self, module_name: str):
        self.module_name = module_name

    def __getattr__(self, attr):
        if attr not in self.__dict__:
            raise ImportError(f"'{self.module_name}' must be installed in order to use this function")
        else:
            return super().__getattribute__(attr)


class DeferredImport:
    __slots__ = (
        '_attr',
        '_module_name',
        '_object',
    )

    """
    Use a DeferredImport when a function requires a particular module or functionality, but
    it is rarely used and slows import time significantly.
    """
    def __init__(self, module_name: str, attr: str = None):
        self._module_name = module_name
        self._attr = attr

        # the object imported
        self._object = None

    def __getattr__(self, attr):
        if self._object is None:
            try:
                self._import()
            except ModuleNotFoundError:
                raise
        return getattr(self._object, attr)

    def _import(self) -> ModuleType:
        mod = importlib.import_module(self._module_name)

        if self._attr is not None:
            self._object = getattr(mod, self._attr)
        else:
            self._object = mod
        return self._object

    def __repr__(self) -> str:
        return repr(self._object)
