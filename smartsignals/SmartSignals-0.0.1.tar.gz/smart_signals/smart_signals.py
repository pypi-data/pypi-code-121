import inspect
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
        """
        Constructor for the SmartSignalSlot

        :param args: The list of data types for slot
        """
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
        """
        Constructor for the Smart Signal

        :param args: The list of data types to be transferred.
        :param name: The name of the signal for logging
        :param multithreading: The multithreading flag to enable multi threading
        """
        self._name = name
        self._multithreading = multithreading
        self._slot_types = args
        self._slots = []

        self._emit_thread: List[threading.Thread] = []

        pass

    def __str__(self) -> str:
        """
        Generate the SmartSignal string

        :return: The SmartSignal string
        """
        elements = list()
        if self._name:
            elements.append(f"name: '{self._name}'")
        elements.append(f"multithreading: '{self._multithreading}'")
        return f"PySignal( {', '.join(elements)} )"

    @property
    def slots(self):
        """
        Return the connected slots

        :return: A list of connected slots
        """
        return self._slots

    def reset(self):
        """
        Resets all connected slots.

        :return: None
        """
        self._slots = []
        pass

    def connect(self, slot):
        """
        Connects the slot to the smart signal.

        :param slot: The slot must be a callable object.
        :return: None
        """
        if not callable(slot):
            raise SmartSignalWrongSlotTypeException(f"The solt: '{slot.__class__.__name__}' is not a callable object!!!")

        if slot not in self._slots:
            self._slots.append(slot)
        pass

    def disconnect(self, slot) -> bool:
        """
        Disconnects the slot from the smart signal.

        :param slot: The solt to be disconnected.
        :return: If the slot could be disconnected, then return True, otherwise return False
        """
        if slot in self._slots:
            self._slots.remove(slot)
            return True
        return False

    def emit(self, *args, **kwargs):
        """
        Calls all connected slots and passes them the args and the kwargs. This function check the types.
        If the multithreading flag has been set, then a thread is created for emitting.

        :param args: Args to emit to the slots
        :param kwargs: Kwargs to emit to the slots
        :return: None
        """
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
