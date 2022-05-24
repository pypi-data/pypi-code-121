from typing import Type, Union


def get_import_code(cls: Type, indent: Union[int, str] = "", alias_inner_class: bool = True) -> str:
    """
    Gets the code to use to import a class.

    :param cls:                 The class.
    :param indent:              The indentation of the code.
    :param alias_inner_class:   Whether to add code to alias inner classes as outer classes.
    :return:                    The code.
    """
    # Can't get import code for closure classes
    if "<locals>" in cls.__qualname__:
        raise ValueError(f"Can't get import code for closure class '{cls.__qualname__}'")

    # Get the outer-most class to import
    outer_class = cls.__qualname__[:cls.__qualname__.index(".")] if "." in cls.__qualname__ else cls.__qualname__

    # Format the indentation string
    if isinstance(indent, int):
        indent = " " * indent

    # Get the code for importing the outer-most class
    code = f"{indent}from {cls.__module__} import {outer_class}"

    # If it's an inner class, alias it
    if cls.__name__ != outer_class and alias_inner_class:
        code += f"\n{indent}{cls.__name__} = {cls.__qualname__}"

    return code
