import inspect
import sys
import threading
from typing import List, _GenericAlias


class SmartSignalWrongSlotTypeException(Exception):
    pass


class SmartSignalWrongDataTypeException(Exception):
    pass


class SmartSlotWrongDataTypeException(Exception):
    pass


class SmartSignalSlot:

    def __init__(self, *args):
        self._slot_types = args
        self._owner = self._get_owner()
        pass

    @classmethod
    def _get_owner(cls) -> str:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        return calframe[2][1]

    def __call__(self, method):
        def wrapped_f(*args, **kwargs):
            if len(args[1:]) != len(self._slot_types):
                raise SmartSlotWrongDataTypeException(f"The number of input parameters: {len(args[1:])} does not match those in the slot definition: {len(self._slot_types)}!")

            if self._slot_types is not None:
                for index, slot_types in enumerate(self._slot_types):
                    arg = args[index + 1]
                    if not isinstance(arg, self._slot_types):
                        raise SmartSlotWrongDataTypeException(f"The object: {arg} is not an instance of '{self._slot_types}', the owner is '{self._owner}'!!")
            method(*args, **kwargs)

        return wrapped_f


class SmartSignal:
    signal_lock = threading.RLock()

    def __init__(self, *args, name: str = None, multithreading: bool = False):
        self._name = name
        self._multithreading = multithreading
        self._slot_types = args
        self._slots = []

        self._emit_thread: List[threading.Thread] = []

        pass

    def __str__(self) -> str:
        elements = list()
        if self._name:
            elements.append(f"name: {self._name})")
        elements.append(f"multithreading: {self._multithreading}")
        return f"PySignal( {', '.join(elements)} )"

    @classmethod
    def _get_sender(cls):
        """Try to get the bound, class or module method calling the emit."""
        prev_frame = sys._getframe(2)
        func_name = prev_frame.f_code.co_name

        # Faster to try/catch than checking for 'self'
        try:
            return getattr(prev_frame.f_locals['self'], func_name)

        except KeyError:
            return getattr(inspect.getmodule(prev_frame), func_name)

    @property
    def slots(self):
        return self._slots

    def reset(self):
        self._slots = []

    def delete_connection(self, slot):
        if slot in self._slots:
            self._slots.remove(slot)

    def emit(self, *args, **kwargs):
        if self._slot_types is not None:
            if len(args) != len(self._slot_types):
                raise SmartSignalWrongDataTypeException(f"The number of input parameters: {len(args)} does not match those in the slot definition: {len(self._slot_types)}!")

            for index, slot_type in enumerate(self._slot_types):
                if isinstance(slot_type, _GenericAlias):
                    container_types = slot_type.__origin__
                    inner_types = slot_type.__args__

                    container = args[index]
                    if not isinstance(container, container_types):
                        raise SmartSignalWrongDataTypeException(f"The container type: '{type(container)}' is incorrect, this type is expected: '{container_types}'")

                    if container_types == list:
                        for element in container:
                            if not isinstance(element, inner_types):
                                raise SmartSignalWrongDataTypeException(f"The list element: '{element}' is not the expected type: '{inner_types}'!!")

                    elif container_types == dict:
                        for key, value in container.items():
                            if not isinstance(key, inner_types[0]):
                                raise SmartSignalWrongDataTypeException(f"The dict key: '{key}' is not the expected key type: '{inner_types[0]}'!!")
                            if not isinstance(value, inner_types[1]):
                                raise SmartSignalWrongDataTypeException(f"The dict value: '{value}' is not the expected value type: '{inner_types[1]}'!!")
                else:
                    if not isinstance(args[index], slot_type):
                        raise SmartSignalWrongDataTypeException(f"An element in the list is of the wrong data type")

        if self._multithreading:
            emit_thread = threading.Thread(target=self._emit_thread_runner, args=args, kwargs=kwargs)
            emit_thread.start()
            self._emit_thread.append(emit_thread)
        else:
            self._emit_thread_runner(*args, **kwargs)
        pass

    def _emit_thread_runner(self, *args, **kwargs):
        for slot in self._slots:
            slot(*args, **kwargs)
        pass

    def connect(self, slot):
        if not callable(slot):
            raise SmartSignalWrongSlotTypeException(f"The solt: '{slot.__class__.__name__}' is not a callable object!!!")

        if slot not in self._slots:
            self._slots.append(slot)
        pass
