"""
Decorator to add an function/method as argument in parser
"""

from polidoro_argument.params import _ArgumentParams


class Argument(object):
    _arguments = []

    def __new__(cls, method=None, **kwargs):
        if callable(method):
            # When the decorator has no arguments
            Argument._arguments.append(_ArgumentParams(method, **kwargs))
            return method
        else:
            # When the decorator has arguments
            def wrapper(_method):
                Argument._arguments.append(_ArgumentParams(_method, **kwargs))
                return _method

            return wrapper
