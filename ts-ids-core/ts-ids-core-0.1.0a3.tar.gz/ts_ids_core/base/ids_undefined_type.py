from typing import Any, Callable, Generator

from pydantic.fields import Undefined as _PydanticUndefinedInstance

from ts_ids_core.annotations import DictStrAny
from ts_ids_core.errors import UndefinedTypeError


class IdsUndefinedType:
    """
    Placeholder indicating that the the value of the :class:`ts_ids_core.base.ids_element.IdsElement`
    field is unknown or non-existent.

    This is distinct from the :class:`ts_ids_core.base.ids_element.IdsElement`'s field
    being ``None``.

    This was partially copied from :class:`pydantic.fields.UndefinedType`. It intentionally
    does not inherit from :class:`pydantic.fields.UndefinedType` so that it fails
    ``isinstance`` and ``issubclass`` checks.
    """

    #: An instance's 'type' in JSON Schema.
    JSON_SCHEMA_TYPE = "Undefined"

    def __repr__(self) -> str:
        return "IdsUndefined"

    def __reduce__(self) -> str:
        """Enable pickling this instance."""
        return self.JSON_SCHEMA_TYPE

    @classmethod
    def __get_validators__(cls) -> Generator[Callable[..., Any], None, None]:
        """
        Yield functions that ``pydantic`` calls during type validation.

        This method must be implemented so :class:`pydantic.BaseModel` fields can have
        :class:`ts_id_core.base.ids_undefined_type.IdsUndefinedType` type.

        See the `pydantic documentation <https://pydantic-docs.helpmanual.io/usage/types/#custom-data-types>`_
        for more info on custom ``pydantic`` field types.
        """
        yield cls.validate

    @classmethod
    def validate(cls, value: Any) -> "IdsUndefinedType":
        """
        Assert that the value is an instance of this class.

        This method is boilerplate for custom ``pydantic`` field types.
        """
        if isinstance(value, cls):
            return value

        raise UndefinedTypeError()

    @classmethod
    def __modify_schema__(cls, field_schema: DictStrAny):
        """
        Return the schema representation of this instance.

        When ``pydantic`` converts this class to JSON Schema via
        :meth:`ts_ids_core.base.ids_element.IdsElement.schema`, an empty dictionary is
        passed in to `field_schema`. Otherwise, if ``field_schema`` remains empty, `pydantic.schema.field_singleton_schema` fails.

        See the [pydantic docs](https://pydantic-docs.helpmanual.io/usage/schema/#modifying-schema-in-custom-fields)
        for further info.
        """
        field_schema["type"] = cls.JSON_SCHEMA_TYPE


#: Sentinel indicating that a field's value is unknown or irrelevant. This is distinct
#: from a field being NULL (`None`).
IDS_UNDEFINED = IdsUndefinedType()
#: By default, `pydantic` passes `default=PYDANTIC_UNDEFINED` to the `Field` function
#: and the `FieldInfo` constructor.
PYDANTIC_UNDEFINED = _PydanticUndefinedInstance
