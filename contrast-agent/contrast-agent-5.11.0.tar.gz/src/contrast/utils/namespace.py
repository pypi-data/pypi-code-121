# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
class Namespace(object):
    """
    Base class for creating module-level namespaces. The purpose of this is to
    circumvent private global variables, which are a hassle. This base class is
    not strictly necessary, but it's a great place for:
    - documentation
    - preventing instantiation of classes used merely as namespaces
    - making the purpose of subclasses very clear when they appear in modules

    An example use case is as follows:

    ```
    class module(Namespace):
        _module_variable_1 = {}
        _module_variable_2 = []
    ```

    Inside of the module, the variables are now available as `module._module_variable_1` etc.
    We suggest the lowercase name `module` for subclasses, as it is a natural extension of
    the `self` and `cls` conventions.

    Compare this globals; modifying a global requires the `global` keyword, which
    is both ugly and easy to forget (making it bug-prone).
    """

    def __new__(cls, *args, **kwargs):
        """
        Prevent instantiation, because that doesn't make sense here
        """
        raise TypeError("Namespace derivatives may not be instantiated")
