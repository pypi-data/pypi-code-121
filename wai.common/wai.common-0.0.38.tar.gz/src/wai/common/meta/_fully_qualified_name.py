from typing import Type


def fully_qualified_name(cls: Type) -> str:
    """
    Gets the fully-qualified name of a class.

    :param cls:     The class.
    :return:        The fully-qualified name.
    """
    return f"{cls.__module__}.{cls.__qualname__}"
