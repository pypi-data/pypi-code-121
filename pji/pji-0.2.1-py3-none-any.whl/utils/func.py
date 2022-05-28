def wrap_empty(func):
    """
    wrap a function which can be None
    :param func: optional function
    :return: final function
    """
    if func:
        return func
    else:
        def _empty_func(*args, **kwargs):
            pass

        return _empty_func
