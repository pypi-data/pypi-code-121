from typing import Any

from pydantic import Field as PydanticField
from pydantic.fields import FieldInfo

from ts_ids_core.base.ids_undefined_type import IDS_UNDEFINED
from ts_ids_core.errors import InvalidConstField


# PascalCase used in function name in order to imitate ``pydantic.Field``, which is
# wrapped by ``IdsField``.
# pylint: disable=invalid-name
def IdsField(default: Any = IDS_UNDEFINED, **kwargs) -> FieldInfo:
    """
    Wrap the :func:`pydantic.Field` function such that, fields default to a sentinel value for
    undefined (a.k.a. unknown or missing) values. As such, the field definition is
    compatible with schema defined using :class:`ts_ids_core.base.ids_element.IdsElement`.

    :param default:
        The default value to use for the field. Default set to a global instance of
        :class:`ts_ids_core.base.ids_undefined_type.IdsUndefinedType` that's intended
        to be used as a singleton.
    :param kwargs:
        All other keyword arguments are passed to :func:`pydantic.Field`.
    :return:
        The resulting :class:`pydantic.fields.FieldInfo` produced by
        :func:`pydantic.Field`.
    """
    if "default_factory" in kwargs and default is not IDS_UNDEFINED:
        raise ValueError("Cannot specify both `default` and `default_factory`.")
    if "const" in kwargs and kwargs["const"] and default is IDS_UNDEFINED:
        raise InvalidConstField(
            "`const` fields must set a default value. If the intent is to create an "
            "abstract field, pass in `default=NotImplemented`."
        )
    if "default_factory" in kwargs:
        # If the default value is set via default_factory, use `pydantic` behavior.
        return PydanticField(**kwargs)
    return PydanticField(default=default, **kwargs)
