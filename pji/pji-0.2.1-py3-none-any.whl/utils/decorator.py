from functools import wraps


def allow_none(func):
    @wraps(func)
    def _func(arg):
        if arg is None:
            return None
        else:
            return func(arg)

    return _func
