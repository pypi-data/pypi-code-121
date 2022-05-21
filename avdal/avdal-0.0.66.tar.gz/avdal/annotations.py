import inspect
import typing as t
from inspect import Parameter


def argmap(f):
    def wrapper(*args, **kwargs):
        sig = inspect.signature(f)

        checks = {}
        sig = inspect.signature(f)
        i = 0
        argc = len(args)
        for k, v in sig.parameters.items():
            if k in kwargs:
                checks[k] = (v.annotation, kwargs[k])
            elif argc > 0:
                checks[k] = (v.annotation, args[i])
                i += 1
                argc -= 1
            else:
                checks[k] = (v.annotation, v.default)

        return checks

    return wrapper


def enforce_types(f: t.Callable) -> t.Callable:
    def wrapper(*args, **kwargs):
        checks = argmap(f)(*args, **kwargs)

        for arg, (annotation, value) in checks.items():
            if annotation == Parameter.empty:
                continue

            if annotation is not any and annotation != type(value):
                fn = f.__name__
                e = annotation.__name__
                a = type(value).__name__

                raise ValueError(f"{fn}: param {arg} expects a value of type {e}, got {a}")

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


def auto_attrs(f: t.Callable) -> t.Callable:
    def wrapper(*args, **kwargs):
        if f.__name__ != "__init__":
            return

        map = argmap(f)(*args, **kwargs)

        if not "self" in map:
            return

        _, self = map["self"]
        del map["self"]

        for arg, (_, value) in map.items():
            setattr(self, arg, value)

        return f(*args, **kwargs)

    wrapper.__name__ = f.__name__
    return wrapper


class Counted:
    def __init__(self, limit, handler=None):
        self.limit = limit
        self.handler = handler

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            if self.limit > 0:
                self.limit -= 1
                return func(*args, **kwargs)
            else:
                if self.handler:
                    return self.handler()

                raise Exception("Reached maximum number of calls")

        return wrapper
