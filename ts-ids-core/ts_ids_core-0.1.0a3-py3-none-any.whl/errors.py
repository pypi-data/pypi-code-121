"""
Exceptions used throughout `ts_ids_core`.

Exception classes derived from `PydanticTypeError` are meant to be raised in the
validator methods of `ts_ids_core.base.ids_element.IdsElement` child classes to
enable `pydantic`-style error messages.
"""
# Disable "missing-class-docstring" because the `msg_template` is equivalent to a
# docstring in classes that derive from :class:`pydantic.errors.PydanticTypeError` and
# :class:`pydantic.errors.PydanticValueError`.
# pylint: disable=missing-class-docstring
# Disable "no-name-in-module" because this is a bug in ``pylint``.
# pylint: disable=no-name-in-module

from pydantic.errors import PydanticTypeError, PydanticValueError


class UndefinedTypeError(PydanticTypeError):
    msg_template = "value is not of type `UndefinedType`"


class MultipleTypesError(PydanticTypeError):
    msg_template = "fields can have only one type other than `None`."


class NotImplementedConstError(PydanticValueError):
    msg_template = "'const' field is not implemented"


class NullableReferenceError(PydanticTypeError):
    msg_template = "fields that contain a reference cannot be nullable"


class WrongConstantError(ValueError):
    """Raised when the user passes a value to an abstract 'const' field."""


class InvalidSchemaMetadata(ValueError):
    """Raised when the IDS' JSON Schema contains an invalid top-level metadata value."""


class InvalidField(Exception):
    """
    Invalid definition for the IDS field.

    Note that this error should only be raised during class creation. Raise errors
    derived from `PydanticTypeError` or `PydanticValueError` for invalid field values,
    e.g. in the body of a `@validator` method.
    """


class InvalidNonMandatoryField(InvalidField):
    """The Non-Mandatory Field of an IDS class is invalid."""


class InvalidConstField(InvalidField):
    """The `const` IDS field type or value is not valid."""
