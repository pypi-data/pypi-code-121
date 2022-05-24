def sequence(*decorators):
    """
    Helper method which creates a decorator that applies the given
    sub-decorators. Decorators are applied in reverse order given.

    @decorator_sequence(dec_1, dec_2, ...)
    def function(...):
        ...

    is equivalent to:

    @dec_1
    @dec_2
    ...
    def function(...):
        ...

    :param decorators:  The sub-decorators.
    :return:            A function which applies the given decorators.
    """
    def apply(obj):
        for dec in reversed(decorators):
            obj = dec(obj)
        return obj

    return apply
