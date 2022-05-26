"""
Module defining the Slot class.
"""
import types
from typing import Any, Callable, Optional
import weakref


class Slot:
    """
    A slot is a callable object that manages a connection to a signal.
    If weak is true or the slot is a subclass of weakref.ref, the slot
    is automatically de-referenced to the called function.
    """

    __slots__ = ["__weak", "__slot"]

    def __init__(self, slot: Callable, weak: bool=True):
        if not callable(slot):
            raise TypeError("A `Slot` instance must be defined from a callable object.")
            
        self.__weak = bool(weak) or isinstance(slot, weakref.ref)
        if weak and not isinstance(slot, weakref.ref):
            if isinstance(slot, types.MethodType):
                slot = weakref.WeakMethod(slot)
            else:
                slot = weakref.ref(slot)
        self.__slot = slot

    @property
    def is_alive(self) -> bool:
        """
        Return `True` if slot is alive, `False` otherwise.
        """
        return (not self.__weak) or (self.__slot() is not None)

    @property
    def func(self) -> Callable:
        """
        Return the function called by slot.
        """
        return self.__slot() if self.__weak else self.__slot

    def __call__(self, **kwargs) -> Optional[Any]:
        """
        Execute slot.
        """
        func = self.func
        if func is not None:
            return func(**kwargs)

    def __eq__(self, other) -> bool:
        """
        Compare this slot to another.
        """
        if isinstance(other, Slot):
            return self.func == other.func
        else:
            return self.func == other

    def __repr__(self) -> str:
        f = self.func
        s = "dead" if f is None else repr(f)
        return f"<cosapp.core.signal.Slot: {s}>"
