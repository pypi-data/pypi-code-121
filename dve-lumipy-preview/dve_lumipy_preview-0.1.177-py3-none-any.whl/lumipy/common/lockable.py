from abc import ABC, abstractmethod


class Lockable(ABC):
    """Abstract base class for immutable objects

    This class implements a locking logic where further alterations using __setattr__ to set attributes or
    __delattr__ to delete them will raise an error. Each inheritor should call the base constructor to lock themselves.
    """

    @abstractmethod
    def __init__(self):
        """
        __init__ method of the lockable abstract base class. Call this in inheritors at the end of their __init__
        method to render them immutable.
        """
        self._locked = True

    def __setattr__(self, key, value):
        # Set to false if it already doesn't exist.
        # Save you having to set it in the ctor each time.
        if not hasattr(self, '_locked'):
            self.__dict__['_locked'] = False

        if self._locked:
            raise TypeError(f"Can't change attributes on {self.__class__.__name__} objects: they are immutable.")

        self.__dict__[key] = value

    def __delattr__(self, item):
        # Set to false if it already doesn't exist.
        # Save you having to set it in the ctor each time.
        if not hasattr(self, '_locked'):
            self.__dict__['_locked'] = False

        if self._locked:
            raise TypeError(f"Can't delete attributes on {self.__class__.__name__} objects: they are immutable.")
