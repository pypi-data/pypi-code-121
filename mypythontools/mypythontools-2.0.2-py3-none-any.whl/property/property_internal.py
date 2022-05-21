"""Module with functions for 'property' subpackage."""

from __future__ import annotations

from typing import Generic, TypeVar, Callable, Type, overload, Any

from typeguard import check_type

from .. import types


T = TypeVar("T")
U = TypeVar("U")


# Needs to inherit from property to be able to use help tooltip
class MyPropertyClass(property, Generic[T]):
    """Python property on steroids. Check module docstrings for more info."""

    # Property is inherited just for formatting help in IDE, so not called from init
    def __init__(self, fget: Callable[..., T], doc=None):  # pylint: disable=super-init-not-called
        """Init property."""
        if fget:
            self.allowed_types = types.get_return_type_hints(fget)

            self.init_function = fget

            if isinstance(fget, staticmethod):
                inner_func = fget.__func__
            else:
                inner_func = fget

            if doc:
                self.__doc__ = doc
            elif inner_func.__doc__:
                self.__doc__ = fget.__doc__
            else:
                self.__doc__ = None

        self.public_name = ""
        self.private_name = ""

    def default_fset(self, used_object, content) -> None:
        """Define how new values will be stored."""
        setattr(used_object, self.private_name, content)

    def __set_name__(self, _, name):
        """Define names. Private usually with underscore."""
        self.public_name = name
        self.private_name = "_" + name

    @overload
    def __get__(self, used_object: None, objtype: Any = None) -> MyPropertyClass[T]:
        ...

    @overload
    def __get__(self, used_object: U, objtype: Type[U] = None) -> T:
        ...

    def __get__(self, used_object, objtype=None):
        """Define what happens when you want access config attribute.

        If used on class, class itself is returned.
        """
        if not used_object:
            return self

        # Expected value can be nominal value or function, that return that value
        content = getattr(used_object, self.private_name)
        if isinstance(content, staticmethod):
            content = content.__func__

        if not hasattr(content, "myproperties_list") and callable(content):
            # Depends whether it's staticmethod or not
            try:
                value = content(used_object)
            except TypeError:
                value = content()

        else:
            value = content

        return value

    def __set__(self, used_object, content: T | Callable[..., T]):
        """Define what happen if user set new config value."""
        # You can setup value or function, that return that value
        if not hasattr(content, "myproperties_list") and callable(content):
            result = content(used_object)
        else:
            result = content

        if self.allowed_types:
            check_type(expected_type=self.allowed_types, value=result, argname=self.public_name)

        self.default_fset(used_object, result)


# Define as static method as it can be used directly
def init_my_properties(self):
    """Init private values of properties.

    Property usually get value of some private variable. This leads to many unnecessary code sometimes.
    """
    if not hasattr(self, "myproperties_list"):
        setattr(self, "myproperties_list", [])

    for i in vars(type(self)).values():
        if isinstance(i, MyPropertyClass):
            self.myproperties_list.append(i.public_name)
            setattr(
                self,
                i.private_name,
                i.init_function,
            )


def MyProperty(f: Callable[..., T]) -> MyPropertyClass[T]:  # pylint: disable=invalid-name
    """Wrap MyProperty to work as expected.

    If not using this workaround, but use class decorator, IDE complains that property has no defined
    setter.

    Args:
        f(Callable[..., T]): Usually it's decorated method from class. It can be static as well.
    """
    return MyPropertyClass[T](f)


# TODO - Use PEP 614 and define type just i n class decorator
# Python 3.9 necessary
