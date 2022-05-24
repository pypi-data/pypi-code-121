from inspect import isclass, ismethod
from types import MethodType
from typing import Type, TypeVar, Union

# Type variable for the instance type
T = TypeVar("T")


class instanceoptionalmethod:
    """
    Decorator class (like classmethod/staticmethod) which provides
    the class as the first implicit parameter, and the instance as
    the second (if called on an instance) or None (if not).
    """
    def __init__(self, function):
        self._function = function

    def __get__(self, instance, owner):
        # Bind the function to the instance/class
        return MethodType(self._function, instance if instance is not None else owner)

    @staticmethod
    def is_instance(self: Union[T, Type[T]]) -> bool:
        """
        Checks if the given reference is an instance or a class.

        :param self:    The instance/class reference.
        :return:        True if the reference is an instance,
                        False if it is a class.
        """
        return not isclass(self)

    @staticmethod
    def type(self: Union[T, Type[T]]) -> Type[T]:
        """
        Helper method which gets the class from self.

        :param self:    The instance/class reference.
        :return:        The class.
        """
        if instanceoptionalmethod.is_instance(self):
            return type(self)

        return self

    @staticmethod
    def will_fail_on_missing_instance(method: MethodType) -> bool:
        """
        Checks if the given "method" call will fail - i.e. the
        "method" is not actually bound. This is useful for when
        an instance-optional method is overridden by an instance-
        required method, but an attempt may be made to call it
        without an instance.

        :return:    True if the method call will fail because it
                    requires an instance which is not present.
        """
        return not ismethod(method)
