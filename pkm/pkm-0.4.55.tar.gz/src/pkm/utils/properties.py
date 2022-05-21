from dataclasses import FrozenInstanceError
from threading import RLock

from typing import TypeVar, Callable, Any, Dict

_T = TypeVar("_T")


# noinspection PyPep8Naming
class cached_property:

    def __init__(self, func: Callable[[Any], _T]):
        self._func = func
        self._attr = None
        self.__doc__ = func.__doc__
        self._mutation_lock = RLock()
        self._instance_locks: Dict[int, RLock] = {}

    def __set_name__(self, owner, name):
        self._attr = f"_cached_{name}"

    def _compute(self, instance):
        compute = True
        iid = id(instance)
        with self._mutation_lock:
            instance_lock = self._instance_locks.get(iid)
            if instance_lock is not None:
                compute = False
            else:
                instance_lock = self._instance_locks[iid] = RLock()
                instance_lock.acquire()

        with instance_lock:
            if compute:
                try:
                    if not hasattr(instance, self._attr):
                        value = self._func(instance)
                        try:
                            setattr(instance, self._attr, value)
                        except FrozenInstanceError:
                            super(instance.__class__, instance).__setattr__(self._attr, value)
                finally:
                    del self._instance_locks[iid]
                    instance_lock.release()

    def __get__(self, instance, owner) -> _T:
        if instance is None:
            return self

        while True:
            try:
                return getattr(instance, self._attr)
            except AttributeError:
                self._compute(instance)

    def __set__(self, instance, value: _T):
        setattr(instance, self._attr, value)

    def __delete__(self, instance):
        if hasattr(instance, self._attr):
            delattr(instance, self._attr)


def clear_cached_properties(obj: Any):
    for attr in dir(obj.__class__):
        if isinstance(getattr(obj.__class__, attr), cached_property):
            delattr(obj, attr)
