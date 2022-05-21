"""Module contains MyProperty class that is alternative to normal python property. It's implemented via
descriptor and edited `__get__` and `__set__` magic methods. 

There is default setter, it's possible to auto init values on class init and values in setter can be
validated. This result in much less code written when using a lot of similar properties.

First call is lazy evaluated during first call.

Example of how can it be used is in module config.

Examples:
=========
    >>> from typing_extensions import Literal
    ...
    >>> class Example:
    ...     def __init__(self) -> None:
    ...         init_my_properties(self)
    ...
    ...     @MyProperty
    ...     def var() -> int:  # Type hints are validated.
    ...         '''
    ...         Type:
    ...             int
    ...
    ...         Default:
    ...             123
    ...
    ...         This is docstrings (also visible in IDE, because not defined dynamically).
    ...         Also visible in Sphinx documentation.'''
    ...
    ...         return 123  # This is initial value that can be edited.
    ...
    ...     @MyProperty
    ...     def var_literal(self) -> Literal[1, 2, 3]:  # Literal options are also validated
    ...         return 2
    ...
    ...     @MyProperty
    ...     def evaluated(self) -> int:  # If other defined value is change, computed property is also updated
    ...         return self.var + 1
    ...
    >>> config = Example()
    >>> config.var
    123
    >>> config.var = 665
    >>> config.var
    665
    >>> config.var = "String is problem"
    Traceback (most recent call last):
    TypeError: ...
    ...
    >>> config.var_literal = 4
    Traceback (most recent call last):
    TypeError: ...
    ...
    >>> config.evaluated
    666
    
    You can still setup a function (or lambda expression) as a new value
    and returned value still will be validated

    >>> config.var = lambda self: self.var_literal + 1
"""

from mypythontools.property.property_internal import MyProperty, init_my_properties

__all__ = ["MyProperty", "init_my_properties"]
