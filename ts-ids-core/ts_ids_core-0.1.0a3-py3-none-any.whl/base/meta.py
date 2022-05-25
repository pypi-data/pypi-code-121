# Disabled because this error is incorrectly raised for all ``from pydantic`` imports.
# pylint: disable=no-name-in-module
import enum
from typing import Any, Callable, Dict, List, NamedTuple, Tuple, Union, no_type_check

from pydantic.fields import FieldInfo, ModelField
from pydantic.json import ENCODERS_BY_TYPE
from pydantic.main import ModelMetaclass
from pydantic.typing import resolve_annotations
from typing_extensions import ClassVar, Type, get_args, get_origin

from ts_ids_core.annotations import DictStrAny, Required
from ts_ids_core.base.ids_field import IdsField
from ts_ids_core.base.ids_undefined_type import (
    IDS_UNDEFINED,
    PYDANTIC_UNDEFINED,
    IdsUndefinedType,
)
from ts_ids_core.errors import InvalidField, MultipleTypesError

__all__ = ["IdsModelMetaclass"]


class IdsFieldCategory(enum.Flag):
    """Indicate the type of an IDS field defined"""

    NULLABLE = enum.auto()
    REQUIRED = enum.auto()


#: A workaround to prevent :class:`ts_ids_core.base.ids_undefined_type.IdsUndefinedType`
#: from breaking :class:`ts_ids_core.base.ids_element.IdsElement.schema`.
ENCODERS_BY_TYPE[IdsUndefinedType] = lambda _: "IdsUndefined"


class RawPydanticField(NamedTuple):
    """
    :ivar name:
        The field name.
    :ivar raw_type_hint:
        The type annotation in the class definition -- i.e. the value associated with
        the field in :attribute:`__annotations__`.
    :ivar raw_value:
        The value that the field is assigned in the class definition. For example,
        consider the following class,

        .. code-block:: python

            from pydantic import BaseModel

            class MyClass(BaseModel):
                foo: str = IdsField()
                bar: str
                baz: str = "BAZ"

        The ``raw_value`` of ``foo`` is the return value of `IdsField()`.

        `bar` is only present in the `__annotations__` of the class and its
        `raw_value` should be :const:`ts_ids_core.base.ids_undefined_type.IDS_UNDEFINED`.

        The `raw_value` associated with the `baz` field should be `"BAZ"`.
    """

    name: str
    raw_type_hint: Type
    raw_value: Any = IDS_UNDEFINED


class ProcessedField(NamedTuple):
    """
    `IdsElement` fields and metadata converted to the form used by `IdsElement`.

    :ivar name:
        The name of the field.
    :ivar category:
        The type of the IDS field. See `IdsFieldCategory` for details.
    :ivar type_hint:
        The type annotation of the field.
    :ivar field_info:
        The `FieldInfo` created using the `name`, `category` and `type_hint` values.
    """

    name: str
    category: IdsFieldCategory
    type_hint: Type
    field_info: FieldInfo


def _separate_required_nullable_type_hints(
    field_type_hint: Type, category: IdsFieldCategory = IdsFieldCategory(0)
) -> Tuple[Type, IdsFieldCategory]:
    """
    Implementation of `separate_required_nullable_type_hints` called recursively.

    See `separate_required_nullable_type_hints` for details.
    """
    origin = get_origin(field_type_hint)
    if origin is Required:
        field_subtype = get_args(field_type_hint)[0]
        category |= IdsFieldCategory.REQUIRED
        return _separate_required_nullable_type_hints(field_subtype, category)
    if origin is Union:
        field_subtypes = set(get_args(field_type_hint))
        if type(None) in field_subtypes:
            category |= IdsFieldCategory.NULLABLE
        else:
            raise MultipleTypesError()
        # Instead of using an `if` statement, first add `type(None)` such that it's
        # guaranteed to be in `field_subtypes`. Then, remove it such that the only
        # remaining type is non-NULL.
        field_subtypes.add(type(None))
        field_subtypes.remove(type(None))
        non_null_subtype = field_subtypes.pop()
        return _separate_required_nullable_type_hints(non_null_subtype, category)
    return field_type_hint, category


def separate_required_nullable_type_hints(
    field_type_hint: Type,
) -> Tuple[Type, IdsFieldCategory]:
    """
    Remove `Required` and `Nullable` from a type hint.

    Note that generics e.g. `Dict` and `Tuple` are not inspected for `Nullable` and
    `Required` types. Thus, `Required` and `Nullable` are only removed from the
    top-level type hint.

    :param field_type_hint:
        The type hint from which to remove `Required` and `Nullable`.
    :return:
        The updated type hint and whether the type hint is `Required` and/or
        `Nullable`, indicated by the `IdsFieldCategory` enum.
    """
    stripped_type_hint, type_category = _separate_required_nullable_type_hints(
        field_type_hint, category=IdsFieldCategory(0)
    )
    return stripped_type_hint, type_category


def _validate_raw_value(raw_value: Any) -> None:
    """
    Some values can be assigned to `pydantic.BaseModel` fields but not to those of IDS
    Schema classes. This function validates that `raw_value` can be used by
    IDS Schema -- i.e. the `IdsElement` class.

    :param raw_value:
        The value assigned to the field in the class definition. See the documentation
        for `RawPydanticField.raw_value` for a more detailed description.
    :raise InvalidField:
        If the value of `raw_value` cannot be parsed into an IDS field.
    """
    if raw_value is Ellipsis:
        raise InvalidField(
            "Whether a field is required should be set via the `Required` type hint, "
            "not using an ellipsis."
        )
    if isinstance(raw_value, FieldInfo) and "required" in raw_value.extra:
        raise InvalidField(
            "Whether a field is required should be set via the `Required` type hint, "
            "not by setting `required`."
        )


def process_raw_field(
    field: RawPydanticField,
) -> ProcessedField:
    """
    Convert the field definition in the class namespace to that usable by `IdsElement`.

    :param field:
        The field in the class definition.

        The attributes of ``field`` are as follows:

        ``name``:
            The name of the variable to which the field is bound.
        ``raw_type_hint``:
            The field's type annotation, processed in such a way as to be usable by
            :class:`ts_ids_core.base.ids_element.IdsElement`.
        ``raw_value``:
            The value assigned to the field prior to processing. See the documentation
            of :attr:`~RawPydanticField.raw_value` for a more detailed description. If a
            field is defined only by a type hint, ``raw_value`` should be
            :const:`ts_ids_core.base.ids_undefined_type.IDS_UNDEFINED`.
    :return:
        The processed field.
    """
    _validate_raw_value(field.raw_value)
    stripped_type_hint, category = separate_required_nullable_type_hints(
        field.raw_type_hint
    )

    field_info = field.raw_value
    if not isinstance(field_info, FieldInfo):
        field_info = IdsField(default=field.raw_value)

    if category & IdsFieldCategory.REQUIRED:
        field_info.extra["required"] = True
    else:
        field_info.extra["required"] = False

    processed_type_hint = stripped_type_hint
    # Required, Nullable
    if category is (IdsFieldCategory.NULLABLE | IdsFieldCategory.REQUIRED):
        processed_type_hint = Union[stripped_type_hint, None]
    elif category is IdsFieldCategory.NULLABLE:  # not Required, Nullable
        processed_type_hint = Union[processed_type_hint, IdsUndefinedType, None]
    elif category is ~(
        IdsFieldCategory.NULLABLE | IdsFieldCategory.REQUIRED
    ):  # not Required, not Nullable
        processed_type_hint = Union[processed_type_hint, IdsUndefinedType]

    # Note: Required, not Nullable type hint does not need to be updated.

    return ProcessedField(
        name=field.name,
        category=category,
        type_hint=processed_type_hint,
        field_info=field_info,
    )


#: Class members that can never be IDS fields.
NON_FIELD_TYPES = (Callable, property, staticmethod, classmethod, type)


def _is_raw_pydantic_field(annotation: Type, field_name: str, raw_value: Any) -> bool:
    """
    Return whether the item in the class namespace is a `pydantic.BaseModel` field.
    """
    if get_origin(annotation) is ClassVar:
        return False
    if field_name.startswith("__"):
        return False
    if isinstance(raw_value, NON_FIELD_TYPES):
        return False
    return True


def get_raw_pydantic_fields(namespace: DictStrAny) -> List[RawPydanticField]:
    """
    Return the :mod:`pydantic` fields in a Python class' namespace.

    :param namespace:
        The namespace of a Python class. This the `namespace` argument typically passed
        to ``type.__new__(mcs, name, bases, namespace, **kwargs)``.
    :return:
        The list of :mod:`pydantic` fields from the namespace.
    """
    ids_class_type_hints = namespace.get("__annotations__", {})
    ids_class_module_name = namespace.get("__module__", None)
    # Resolve forward references.
    original_annotations = resolve_annotations(
        raw_annotations=ids_class_type_hints, module_name=ids_class_module_name
    )
    return [
        RawPydanticField(
            name=field_name,
            raw_type_hint=annotation,
            # fmt: off
            raw_value=namespace.get(
                # pylint: disable because this usage is intended for ``NamedTuple``.
                # See https://docs.python.org/3/library/collections.html#collections.somenamedtuple._field_defaults
                field_name, RawPydanticField._field_defaults["raw_value"],  # pylint: disable=no-member,protected-access
            ),
            # fmt: on
        )
        for field_name, annotation in original_annotations.items()
        if _is_raw_pydantic_field(
            annotation, field_name, namespace.get(field_name, IDS_UNDEFINED)
        )
    ]


class IdsModelMetaclass(ModelMetaclass):
    """
    Extension of :class:`pydantic.main.ModelMetaclass` enabling "required" and
    "nullable" fields, as defined for IDS.
    """

    __fields__: Dict[str, ModelField]

    @no_type_check
    # First argument is named 'mcs' to clarify that it's a metaclass, not the
    # returned class.
    # pylint: disable=bad-classmethod-argument
    def __new__(
        mcs,
        name: str,
        bases: Tuple[Type, ...],
        namespace: DictStrAny,
        **kwargs: Any,
    ) -> "IdsModelMetaclass":

        """
        :param name:
            The name of the class to be created.
        :param bases:
            The base classes from which the class is derived, in method-resolution order.
        :param namespace:
            See the class docstring for further info.
        """
        raw_fields = get_raw_pydantic_fields(namespace)
        processed_raw_fields = [process_raw_field(field) for field in raw_fields]
        annotations = namespace.get("__annotations__", {})
        annotations.update(
            {field.name: field.type_hint for field in processed_raw_fields}
        )
        namespace.update(
            {field.name: field.field_info for field in processed_raw_fields}
        )
        cls = super(IdsModelMetaclass, mcs).__new__(
            mcs, name, bases, namespace, **kwargs
        )
        # Assert that the `schema_extra_metadata` field is not an IDS field because
        # `schema_extra_metadata` is a reserved name.
        if "schema_extra_metadata" in cls.__fields__:
            raise InvalidField(
                "`schema_extra_metadata` is reserved for JSON Schema metadata and thus "
                "cannot be an IDS field name."
            )

        for field_name in cls.__fields__:
            model_field = cls.__fields__[field_name]
            # Assert that either the `ModelField` instance has already defined `required`
            # e.g. via inheritance, or that the `FieldInfo`'s "required" value was set
            assert (
                "required" in model_field.field_info.extra
                or model_field.required is not PYDANTIC_UNDEFINED
            ), f"Field '{field_name}' did not properly set its 'required' property."
            model_field.required = model_field.field_info.extra.pop(
                "required", model_field.required
            )
            if model_field.field_info.default_factory is None:
                model_field.default = model_field.field_info.default

        return cls
