def expose_method(parameters=None):
    """
    Use this decorator for any devices method.

    The decorated function will be exposed to the client.

    Example::

        @expose_method({"position": "Relative position"})
        def move_relative(self, position):
        ...

    :param parameters: dict(Exposed param1: Description, Exposed param2: Description, ...)
    :return: decorated function
    """

    def decorator(fun):
        setattr(fun, "exposed_parameters", parameters)
        # fun.exposed_parameters = parameters
        return fun

    return decorator
