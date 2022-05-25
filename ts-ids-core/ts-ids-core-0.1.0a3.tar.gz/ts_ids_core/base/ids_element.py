from itertools import repeat
from typing import (
    AbstractSet,
    Any,
    Callable,
    ClassVar,
    Container,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Type,
    Union,
)

from pydantic import BaseModel, Extra, validator
from pydantic.errors import MissingError
from pydantic.fields import ModelField
from pydantic.schema import default_ref_template
from typing_extensions import Literal, final, get_args, get_origin

from ts_ids_core.annotations import AbstractSetIntStr, DictStrAny, MappingIntStrAny
from ts_ids_core.base.ids_undefined_type import IDS_UNDEFINED, IdsUndefinedType
from ts_ids_core.base.meta import IdsModelMetaclass
from ts_ids_core.errors import (
    InvalidConstField,
    InvalidSchemaMetadata,
    NotImplementedConstError,
    NullableReferenceError,
    WrongConstantError,
)

SchemaExtraMetadataType = ClassVar[Dict[str, Union[str, int, float]]]
FieldsFilterType = Union[AbstractSetIntStr, MappingIntStrAny, None]


#: Base class for IDS classes.
class IdsElement(BaseModel, metaclass=IdsModelMetaclass):
    _INVALID_SCHEMA_CONST_VALUES: ClassVar[Set] = {NotImplemented, IDS_UNDEFINED}
    #: Key/value pairs to add to the JSON Schema. These values will not be in the
    #: output of method :meth:`~IdsElement.dict` nor :meth:`~IdsElement.json`. That is,
    #: they won't be in the IDS instance. To indicate that the
    #: key/value pair is abstract and thus expected to be overridden by the child class,
    #: set the value to :const:`NotImplemented`.
    #: Note that in child classes the :any:`typing.ClassVar` type hint must be
    #: provided in order to indicate that ``schema_extra_metadata`` is not an IDS Field.
    schema_extra_metadata: SchemaExtraMetadataType = {}

    def __init__(__pydantic_self__, **data) -> None:
        """
        Set each field's value to its default if no value was passed to the constructor.

        :param data:
            See the base class' docstring.
        """
        # Set the value of each element to the default value, if no value is passed to
        # the constructor. This is required to prevent the base class,
        # ``pydantic.BaseModel``, from passing in ``pydantic.Undefined``.
        for field_name, field in __pydantic_self__.__class__.__fields__.items():
            if field_name not in data:
                data[field_name] = field.get_default()
        super().__init__(**data)

    class Config:
        """
        Configuration class. See the `pydantic documentation <https://pydantic-docs.helpmanual.io/usage/model_config/#options>`_ for further info.
        """

        #: See the `pydantic docs <https://pydantic-docs.helpmanual.io/usage/model_config/#options>`_
        #: for documentation on constants below.
        use_enum_values = True
        extra = Extra.forbid
        allow_population_by_field_name = True
        json_encoders = {IdsUndefinedType: lambda v: v.__reduce__()}

        @staticmethod
        @final
        def schema_extra(schema: DictStrAny, model: Type["IdsElement"]) -> None:
            """
            Post-process schema prior to return from
            :meth:`ts_ids_core.base.ids_element.IdsElement.schema`.

            :param schema:
                The JSON Schema.
            :param model:
                The class from which the schema is generated.
            :return:
                None. ``schema`` is modified in-place.
            """
            model.Config._format_schema_types(schema, model)
            model.Config._remove_keys_from_schema(
                schema, {"title", "format", "default"}
            )
            assert hasattr(model, "schema_extra_metadata")
            schema.update(model.schema_extra_metadata.copy())

        @classmethod
        def _remove_keys_from_schema(
            cls, schema: DictStrAny, keys: Iterable[str]
        ) -> None:
            """
            Remove the provided keys from the top level, "properties" field and
            "definitions" fields.
            """
            properties = schema.get("properties", dict())
            definitions = schema.get("definitions", dict())

            for key in keys:
                for _, value in properties.items():
                    value.pop(key, None)
                for _, value in definitions.items():
                    cls._remove_keys_from_schema(value, keys)
                schema.pop(key, None)

        @staticmethod
        def _format_schema_types(schema: DictStrAny, model: Type["BaseModel"]) -> None:
            """
            1. If the type hint is `Nullable[T]`, set the JSON Schema type to [T, "null"].
               If the type hint is `None`, set the JSON Schema type to ["null"].
            2. If the field is not `Required`, the `IdsElement`'s field will have type
              `Union[..., IdsUndefinedType]`. `_format_schema_types` removes
              `IdsUndefinedType` from the JSON Schema's types.
            3. Put the "$ref" field in the right place.
            """

            def _set_field_types(_properties: DictStrAny) -> None:
                """Replace `allOf` and `anyOf` field specification with "type": [...]."""
                allof_or_anyof_types = []  # type: List[DictStrAny]
                assert not ("anyOf" in _properties and "allOf" in _properties)
                allof_or_anyof_types.extend(_properties.pop("anyOf", dict()))
                allof_or_anyof_types.extend(_properties.pop("allOf", dict()))

                for subtypes in allof_or_anyof_types:
                    subtypes: DictStrAny
                    if "$ref" in subtypes:
                        # If there's no 'type' key that's not 'Undefined', the only other
                        # key will be '$ref'.
                        _properties["$ref"] = subtypes["$ref"]
                        break

                    # Skip if the 'type' key is missing or if the 'type' is
                    # `ts_ids_core.base.meta.IDS_UNDEFINED`. Otherwise, if the
                    # 'anyOf' or 'allOf' value is an atomic type, add it
                    # to `_properties`. Note that, there should only ever be one type
                    # other than `IDS_UNDEFINED`.
                    # fmt: off
                    if subtypes.get('type', IdsUndefinedType.JSON_SCHEMA_TYPE) != IdsUndefinedType.JSON_SCHEMA_TYPE:
                        assert "type" not in _properties, \
                            "Caution: overwriting schema type. This should not be possible " \
                            "if the field is consistent with the IDS convention that fields " \
                            "have only one type."
                        _properties.update(subtypes)
                    # fmt: on

            def _update_schema_of_nullable_fields(
                _properties: DictStrAny,
                _field: ModelField,
            ) -> None:
                """
                Update a JSON Schema `object` field so its type is consistent with
                Python type annotation.

                Note that, when defining a `pydantic.BaseModel` class, `Union[T, None]`
                field type hints result in the `ModelField.type_` getting set to `T`.
                Note that a `Union[S, T, None]` type hint does not have this issue; that
                is, the instance's `ModelField.type_` is `Union[S, T, None]`.

                To indicate that the field may take on the value of `None`, `pydantic`
                sets the `pydantic.ModelField.allow_none` instance to `True`. Therefore,
                to determine whether to set the JSON Schema type to "null", both the
                `pydantic.ModelField.allow_none` and the `pydantic.ModelField.type_` must
                be accounted for.

                :param _properties:
                    The `properties` section of the JSON Schema to update in place.
                :param _field:
                    The field to update the JSON Schema for.
                """

                def _is_type_nullable(python_type_hint: Type) -> bool:
                    """Determine whether `python_type_hint` allows `None`."""
                    outer_type = get_origin(python_type_hint)
                    if outer_type in (Union, Literal):
                        subtypes = get_args(python_type_hint)
                        for subtype in subtypes:
                            if subtype is type(None):
                                return True
                            if get_origin(subtype) is not None:
                                return any(
                                    _is_type_nullable(type_)
                                    for type_ in get_args(subtype)
                                )
                        return False
                    elif python_type_hint is None:
                        return True
                    return False

                # There's no easy way to allow a nullable reference, so we won't allow it at all
                if "$ref" in _properties and _is_type_nullable(_field.type_):
                    raise NullableReferenceError()

                if "type" not in _properties:
                    return
                if _properties["type"] == "array":
                    # fmt: off
                    assert _field.sub_fields is not None, "`ModelField.sub_fields` not specified"
                    assert len(_field.sub_fields) > 0, "`ModelField.sub_fields` is empty"
                    # fmt: on
                    _subfield = next(
                        _subfield
                        for _subfield in _field.sub_fields
                        if _subfield.type_ is not IdsUndefinedType
                    )
                    _update_schema_of_nullable_fields(
                        _properties["items"], _field=_subfield
                    )
                    return
                if _properties["type"] == IdsUndefinedType.JSON_SCHEMA_TYPE:
                    # If the field's type is `None` and the field is Not Required
                    _properties["type"] = ["null"]
                    return
                if _field.allow_none or _is_type_nullable(_field.type_):
                    # If the field's type is Nullable[T], then its schema type is [T, "null"].
                    _properties["type"] = [_properties["type"], "null"]
                    if "enum" in _properties:
                        # If the field is an Enum
                        _properties["enum"].append(None)

            properties = schema.get("properties", {})
            for subfield in model.__fields__.values():
                _set_field_types(properties[subfield.alias])
                _update_schema_of_nullable_fields(properties[subfield.alias], subfield)

    @validator("*", pre=True)
    def all_required_fields_defined(cls, value: Any, field: ModelField) -> Any:
        """Assert that all required fields are assigned a value."""
        if field.required and value is IDS_UNDEFINED:
            raise MissingError()
        return value

    @validator("*", pre=True)
    def all_const_fields_implemented(cls, value: Any, field: ModelField) -> Any:
        """Assert no ``const`` field values are :const:`NotImplemented`."""
        if field.field_info.const and value is NotImplemented:
            raise NotImplementedConstError()
        if field.field_info.const and field.default is NotImplemented:
            raise WrongConstantError(
                f"This field is abstract, but was passed the value, '{str(value)}'."
            )
        return value

    @classmethod
    def schema(
        cls, by_alias: bool = True, ref_template: str = default_ref_template
    ) -> "DictStrAny":
        """
        Return the JSON Schema as a Python object.

        :param by_alias:
            Whether to use field aliases in the JSON Schema. Defaults to `True`.
        :param ref_template:
            The ``$ref`` template. Defaults to '#/definitions/{model}', where ``model`` is replaced
            with the :class:`ts_ids_core.base.ids_element.IdsElement`'s class name.
        :return:
            The JSON Schema, as described above.
        :raise InvalidConstField:
            One or more ``const`` field(s) are not defined.
        :raise InvalidSchemaMetadata:
            One or more of the schema metadata fields specified in
            :attribute:`ts_ids_core.base.ids_element.schema_extra_metadata` are invalid values.
        """
        invalid_const_fields = [
            field_name
            for field_name, field in cls.__fields__.items()
            if field.default in cls._INVALID_SCHEMA_CONST_VALUES
            and field.field_info.const
        ]
        if len(invalid_const_fields) > 0:
            raise InvalidConstField(
                f"Invalid schema because the following 'const' field values are not "
                f"defined: {', '.join(invalid_const_fields)}"
            )
        invalid_extra_metadata_fields = [
            metadata_key
            for metadata_key, metadata_value in cls.schema_extra_metadata.items()
            if metadata_value is NotImplemented
        ]
        if len(invalid_extra_metadata_fields) > 0:
            raise InvalidSchemaMetadata(
                f"Invalid schema because the following schema metadata fields are not "
                f"implemented: {', '.join(invalid_extra_metadata_fields)}. Set their values using "
                f"the `schema_extra_metadata` class variable."
            )

        return super().schema(by_alias=by_alias, ref_template=ref_template)

    @property
    def undefined_fields(self) -> Set[str]:
        """The set of field names whose values are not defined."""
        return {
            field_name
            for field_name in self.__fields__
            if getattr(self, field_name) is IDS_UNDEFINED
        }

    def dict(
        self,
        *,
        include: FieldsFilterType = None,
        exclude: FieldsFilterType = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = None,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> "DictStrAny":
        """
        Export to a Python dictionary, excluding any fields whose values are not defined.

        See base class for more in-depth description of parameters other than
        ``exclude_unset``.

        :param exclude_unset:
            This parameter is not used but is maintained in order to preserve the parent
            class' API.
        :raise NotImplementedError:
            If any value other than the default is passed to ``exclude_unset``. The
            ``exclude_unset`` parameter is only to keep the API consistent with
            the parent class' method, :meth:`pydantic.BaseModel.dict`.
        """
        self._raise_if_not_value(
            None,
            exclude_unset,
            NotImplementedError,
            "Passing `exclude_unset=True` is not implemented.",
        )
        fields_to_exclude = self._get_excluded_fields(self.undefined_fields, exclude)
        return super().dict(
            include=include,
            exclude=fields_to_exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
        )

    def json(
        self,
        *,
        include: FieldsFilterType = None,
        exclude: FieldsFilterType = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = None,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        encoder: Optional[Callable[[Any], Any]] = None,
        models_as_dict: bool = True,
        **dumps_kwargs: Any,
    ) -> str:
        """
        Export to JSON.

        See base class for more in-depth description of parameters other than
        ``exclude_unset``.

        :param exclude_unset:
            This parameter is not used but is maintained in order to preserve the parent
            class' API.
        :raise NotImplementedError:
            If any value other than the default is passed to ``exclude_unset``. The
            ``exclude_unset`` parameter is only to keep the API consistent with
            the parent class' method, :meth:`pydantic.BaseModel.json`.
        """
        self._raise_if_not_value(
            None,
            exclude_unset,
            NotImplementedError,
            "Passing `exclude_unset=True` is not implemented.",
        )
        fields_to_exclude = self._get_excluded_fields(self.undefined_fields, exclude)
        return super().json(
            include=include,
            exclude=fields_to_exclude,
            by_alias=by_alias,
            skip_defaults=skip_defaults,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            encoder=encoder,
            models_as_dict=models_as_dict,
            **dumps_kwargs,
        )

    @staticmethod
    def _raise_if_not_value(
        expected_value: Any,
        actual_value: Any,
        error_type: Type[Exception],
        message: Optional[str],
    ) -> None:
        """Raise the desired error if `expected_value` does not equal `actual_value`."""
        if actual_value != expected_value:
            raise error_type(message)

    @staticmethod
    def _get_excluded_fields(
        undefined_fields: Set[str], extra_excluded_fields: FieldsFilterType
    ) -> MappingIntStrAny:
        """
        Return the fields that should be excluded from the output of the `dict` and `json` methods.

        :param undefined_fields:
            Fields whose field is :const:`ts_ids_core.base.ids_undefined_type.IDS_UNDEFINED`.
        :param extra_excluded_fields:
            If ``extra_excluded_fields`` is a set add these fields to the returned dictionary, mapped
            to ``True`` to indicate these fields should be excluded.
            If ``extra_excluded_fields`` is a mapping, its values may be booleans, in which case
            add the associated keys to the fields to be excluded. Alternatively, the values in
            ``extra_excluded_fields`` may be a mappings of subfields or subfield indices to exclude. See the
            `pydantic docs <https://pydantic-docs.helpmanual.io/usage/exporting_models/#advanced-include-and-exclude>`_
            for details.
        :return:
            See the summary docstring above.
        """
        parsed_extra_excluded_fields = extra_excluded_fields
        if isinstance(extra_excluded_fields, AbstractSet):
            parsed_extra_excluded_fields = {key: True for key in extra_excluded_fields}
        elif extra_excluded_fields is None:
            parsed_extra_excluded_fields = dict()

        # The following lines of code check whether `extra_excluded_fields`
        # conflict with `undefined_fields`, i.e. if `extra_excluded_fields` says to exclude
        # a field but the field's value is `IDS_UNDEFINED`.
        invalid_fields_to_exclude = undefined_fields.intersection(
            {
                excluded_field
                for excluded_field, is_excluded in parsed_extra_excluded_fields.items()
                if is_excluded is False
                or (isinstance(is_excluded, Container) and bool(is_excluded))
            }
        )
        if len(invalid_fields_to_exclude) > 0:
            raise ValueError(
                f"The following fields in the `exclude` argument contain undefined fields: "
                f"{', '.join(invalid_fields_to_exclude)}"
            )

        return dict(zip(undefined_fields, repeat(True)), **parsed_extra_excluded_fields)
