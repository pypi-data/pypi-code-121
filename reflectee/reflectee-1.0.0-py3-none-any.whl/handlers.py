from pathlib import Path

from django.utils.module_loading import import_string

__all__ = ["handlers", "register", "loads"]

handlers = {}


def loads(api_path):
    for path in Path(api_path).rglob("*.py"):
        event = str(path)[len(api_path) + 1 : -3]
        module_name = str(path).replace("/", ".")[0:-3]
        try:
            handler = import_string(module_name + ".handle")
        except ImportError as e:
            handler = None
            print(e)
        if handler:
            _register(event, handler)


def _register(event: str, handler):
    if event not in handlers:
        handlers[event] = handler
    else:
        raise Exception(f"{event} already registered")


def register(event: str):
    def wrapper(handler):
        _register(event, handler)
        return handler

    return wrapper
