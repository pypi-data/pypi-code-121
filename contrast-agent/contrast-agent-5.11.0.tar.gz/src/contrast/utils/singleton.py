# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
class Singleton(object):
    """
    Base class for children that provide the Singleton pattern

    Singletons are classes that guarantee that only a single instance can ever
    be created. Any time a "new" instance of the class is instantiated, it
    actually refers to the same underlying object. This is useful for providing
    a container for global state.

    This implementation was taken from the Python documentation (admittedly,
    from a very old version):
        https://www.python.org/download/releases/2.2/descrintro/#__new__
    """

    def __new__(cls, *args, **kwds):
        instance = cls.__dict__.get("__instance__")
        if instance is not None:
            return instance

        cls.__instance__ = instance = object.__new__(cls)
        instance.init(*args, **kwds)
        return instance

    def init(self, *args, **kwds):
        """
        Subclasses should override this method for initialization, and not __init__.
        """
        pass

    @classmethod
    def clear_instance(cls):
        """
        Delete the singleton's current instance.

        While singletons are objects intended to have one instance only, there
        may be time when deleting the existing instance is needed.
        """
        instance = cls.__dict__.get("__instance__")
        if instance is not None:
            del cls.__instance__
