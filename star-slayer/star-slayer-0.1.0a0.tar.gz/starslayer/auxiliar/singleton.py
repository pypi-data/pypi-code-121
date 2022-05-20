"""
Singleton Module. Contains the Singleton metaclass.
"""

class Singleton(type):
    """
    Singleton metaclass.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Calls this object as a function.
        """

        if cls not in cls._instances:

            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]
