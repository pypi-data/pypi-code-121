"""
Module defining the Signal class.
"""

import inspect
import logging
import threading
from typing import Any, Callable, List, Optional, Union

from cosapp.core.signal.slot import Slot

logger = logging.getLogger(__name__)


class DummyLock:
    """
    Class that implements a no-op instead of a re-entrant lock.
    """

    def __enter__(self):
        pass

    def __exit__(self, exc_type=None, exc_value=None, traceback=None):
        pass


class Signal:
    """
    Define a signal by instanciating a :py:class:`Signal` object, ie.:

    >>> conf_pre_load = Signal()

    Optionaly, you can declare a list of argument names for this signal, ie.:

    >>> conf_pre_load = Signal(args=['conf'])

    Any callable can be connected to a Signal, it **must** accept keywords
    (``**kwargs``) and be wrapped in a `Slot` object, ie.:

    >>> def yourmodule_conf(conf, **kwargs):
    ...     conf['yourmodule_option'] = 'foo'
    ...

    Connect your function to the signal using :py:meth:`connect`:

    >>> conf_pre_load.connect(Slot(yourmodule_conf))

    Emit the signal to call all connected callbacks using
    :py:meth:`emit`:

    >>> conf = {}
    >>> conf_pre_load.emit(conf=conf)
    >>> conf
    {'yourmodule_option': 'foo'}

    Note that you may disconnect a callback from a signal if it is already
    connected:

    >>> conf_pre_load.is_connected(yourmodule_conf)
    True
    >>> conf_pre_load.disconnect(yourmodule_conf)
    >>> conf_pre_load.is_connected(yourmodule_conf)
    False
    """

    def __init__(
        self,
        args: Optional[List[str]] = None,
        name: Optional[str] = None,
        threadsafe: bool = False,
    ) -> None:
        self.__slots = []
        self.__slot_lock = threading.RLock() if threadsafe else DummyLock()
        self.args = args or []
        self.name = name

    @property
    def slots(self) -> List[Slot]:
        """
        Return a list of slots for this signal.
        """
        with self.__slot_lock:
            # Do a slot clean-up
            slots = []
            for s in self.__slots:
                if isinstance(s, Slot) and (not s.is_alive):
                    continue
                slots.append(s)
            self.__slots = slots
            return list(slots)

    def connect(self, slot: Union[Slot, Callable]) -> None:
        """
        Connect a callback `slot` to this signal.
        """
        if not isinstance(slot, Slot):
            try:
                slot = Slot(slot)
            except TypeError:
                raise TypeError("Only callable objects can be connected to a Signal.")

        # Check function accept kwargs
        if len(self.args) > 0 and inspect.getfullargspec(slot.func).varkw is None:
            raise TypeError("'slot' function must accept keyword arguments.")

        with self.__slot_lock:
            if not self.is_connected(slot):
                self.__slots.append(slot)

    def is_connected(self, slot: Slot) -> bool:
        """
        Check if a callback `slot` is connected to this signal.
        """
        with self.__slot_lock:
            return slot in self.__slots

    def disconnect(self, slot: Slot) -> None:
        """
        Disconnect a slot from a signal if it is connected; else do nothing.
        """
        with self.__slot_lock:
            if self.is_connected(slot):
                self.__slots.pop(self.__slots.index(slot))

    def emit(self, **kwargs) -> Optional[Any]:
        """
        Emit signal, which will execute every connected callback `slot`,
        passing keyword arguments.

        If a slot returns anything other than None, then :py:meth:`emit` will
        return that value preventing any other slot from being called.

        >>> need_something = Signal()
        >>> def get_something(**kwargs):
        ...     return 'got something'
        ...
        >>> def make_something(**kwargs):
        ...     print('I will not be called')
        ...
        >>> need_something.connect(get_something)
        >>> need_something.connect(make_something)
        >>> need_something.emit()
        'got something'
        """
        for slot in self.slots:
            try:
                result = slot(**kwargs)
            except Exception as err:
                logger.exception(" ".join(repr(err).splitlines()))
            else:
                if result is not None:
                    return result

    def __eq__(self, other: Union[Slot, Callable]) -> bool:
        """
        Return True if other has the same slots connected.

        >>> a = Signal()
        >>> b = Signal()
        >>> a == b
        True
        >>> def slot(**kwargs):
        ...    pass
        ...
        >>> a.connect(slot)
        >>> a == b
        False
        >>> b.connect(slot)
        >>> a == b
        True
        """
        return self.slots == other.slots

    def __repr__(self) -> str:
        return f"<cosapp.core.signal.Signal: {self.name or 'NO_NAME'}>"
