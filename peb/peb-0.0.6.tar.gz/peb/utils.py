def raise_or(e, value, throw=False):
    if throw:
        raise e
    return value


def safeaccess(obj, *args, context=None, default=None):
    if obj is None:
        return default

    context = context or dict()
    value = obj

    for arg in args:
        value = getattr(value, arg)
        if value is None:
            return default
        if callable(value):
            value = value(**context)

    return value
