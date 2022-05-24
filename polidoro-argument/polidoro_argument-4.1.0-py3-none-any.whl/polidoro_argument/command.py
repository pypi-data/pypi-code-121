"""
Decorator to add an function/method as command in parser
"""

from polidoro_argument.params import _CommandParams


class Command(object):
    _commands = {}

    def __new__(cls, method=None, **kwargs):
        if callable(method):
            # When the decorator has no arguments
            Command.add_command(method, **kwargs)
            return method
        else:
            # When the decorator has arguments
            def wrapper(_method):
                Command.add_command(_method, **kwargs)
                return _method

            return wrapper

    @staticmethod
    def get_command(item):
        # Return the Argument with the same name as item ou same method
        for c in Command._commands.values():
            if item in [c.method_name, c.method]:
                return c

    @staticmethod
    def add_command(method, **kwargs):
        if method.__qualname__ in Command._commands:
            print(f'WARNING: Command "{method.__qualname__}" already defined. Ignoring...')
        else:
            Command._commands[method.__qualname__] = (_CommandParams(method, **kwargs))
