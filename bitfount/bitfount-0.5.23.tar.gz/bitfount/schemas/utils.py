"""Module for serialization and deserialization of models, algorithms and protocols."""
import itertools
from pathlib import Path
from typing import Any, Mapping, Optional, Tuple, Type, Union, cast

from marshmallow import Schema as MarshmallowSchema
from marshmallow import fields, post_load

from bitfount.federated.model_reference import BitfountModelReference
from bitfount.models.base_models import CNNModelStructure
from bitfount.schemas.exceptions import SchemaClassError
from bitfount.types import _JSONDict

# Methods for dumping the schema
# In bf_dump, we take an object which we convert to a schema using the
# `_obj_to_schema` function. For each item provided in to the
# `_obj_to_schema` function we also have to load all attributes
#  of the parent classes,which we do using `_bf_combine_dict_dump.


def bf_dump(bf_obj: Any) -> _JSONDict:
    """Method for serializing an object.

    Args:
        bf_obj: The object we want to generate the schema dump for.

    Raises:
        SchemaClassError: if the provided object is None.
    """
    # Get the schema class from the object.
    schema_cls = _obj_to_schema(bf_obj)

    if schema_cls is None:
        raise SchemaClassError(
            f"There is no schema class that can be "
            f"generated from the given object:{bf_obj}."
        )
    else:
        myschema = schema_cls()

        # Get the schema dump
        schema_dump = cast(_JSONDict, myschema.dump(bf_obj))
        # Make sure all fields and the schema are deleted to prevent
        # memory leak.
        del myschema

        return schema_dump


def _obj_to_schema(bf_obj: Any, depth: int = 0) -> Optional[Type[MarshmallowSchema]]:
    """Converts an object to a marshmallow schema."""
    if depth > 5:
        raise SchemaClassError("Cannot have more than depth 5 in serialisation")

    if bf_obj:
        # Load all nested and unnested attributes of the parent classes.
        unnested_fields, nested_fields = _bf_combine_dict_dump(
            bf_obj, bf_obj.fields_dict.copy(), bf_obj.nested_fields.copy()
        )
        unnested_fields["class_name"] = fields.Str()
        nested_fields_helper = {}

        # For each nested item, go recursively through them and unpack
        # to only have unnested fields and then generate schemas for
        # all of them.
        for k, _ in nested_fields.items():
            aux = {}
            # We only care about the case when `_obj_to_schema` is no None
            if _obj_to_schema(getattr(bf_obj, k), depth + 1) is not None:
                aux = {k: _obj_to_schema(getattr(bf_obj, k), depth + 1)}
            nested_fields_helper.update(aux)

        # Get the schema of the object
        return _get_marshmallow_schema(
            bf_obj.__class__, unnested_fields, nested_fields_helper
        )
    else:
        return None


def _bf_combine_dict_dump(
    cls: Any, fields_dict: _JSONDict, nested_fields: _JSONDict
) -> Tuple[_JSONDict, _JSONDict]:
    """Combine the nested and unnested fields from the subclasses.

    Loop through the class mro, and get the fields_dict and
    nested_fields from the parent classes.
    """
    for item in cls.__class__.__mro__:
        fields_dict, nested_fields = _combine_dict_helper(
            cls, item, fields_dict, nested_fields
        )
    return fields_dict, nested_fields


# Shared Methods


def _get_marshmallow_schema(
    obj_class: Any,
    unnested_fields: _JSONDict,
    nested_schemas: _JSONDict,
) -> Type[MarshmallowSchema]:
    """Generate the marshmallow schema from field dictionaries."""
    # For all nested items, define them as a nested field with the generated schema.
    nested = ((name, fields.Nested(value)) for (name, value) in nested_schemas.items())

    @post_load
    def recreate_factory(self: Any, data: _JSONDict, **_kwargs: Any) -> Any:
        data = data.copy()
        data.pop("class_name")
        return obj_class(**data)

    # Pack all fields needed for the schema generation
    all_fields = dict(
        itertools.chain.from_iterable(
            [
                nested,
                unnested_fields.items(),
                [(recreate_factory.__name__, recreate_factory)],
            ]
        )
    )
    # Get the return schema from the fields.
    ReturnSchema = _BitfountGeneratedSchema.from_dict(all_fields)
    return ReturnSchema


class _BitfountGeneratedSchema(MarshmallowSchema):
    """Schema class to prevent registering all the Marshmallow Schemas generated."""

    class Meta:
        """Meta class for the _BitfountGeneratedSchema.

        Used to set the register to `False`, to make sure that the newly generated
        schemas are not registered in the marshmallow class registers.
        """

        register = False

    def __del__(self) -> None:
        """Helper function for deleting all schema attributes.

        It makes sure that all the fields are assigned to None
        when schema gets deleted, to free up memory.
        """
        # Mypy complains that there is a type mismatch between these
        # fields and `None` type, however, our goal is to make sure
        # they are set to None when deleting the schema, so we can
        # ignore the assignment.
        self.fields = None  # type: ignore[assignment] # Reason: see above
        self.declared_fields = None  # type: ignore[assignment] # Reason: see above # noqa: B950
        self.load_fields = None  # type: ignore[assignment] # Reason: see above
        self.dump_fields = None  # type: ignore[assignment] # Reason: see above

    # The below methods are related to the `BitfountModelReference`.
    # They are used for serialization and deserialization of the model_ref.
    # The marshmallow field for the model_ref is using these methods for
    # serializing/ deserializing.
    @staticmethod
    def get_model_ref(bfmr: BitfountModelReference) -> str:
        """Returns the model_ref, ready for serialization.

        Used for serialization of BitfountModelReference.
        """
        model_ref = bfmr.model_ref
        try:
            return model_ref.stem  # type: ignore[union-attr]  # Reason: captured by AttributeError below  # noqa: B950
        except AttributeError as ae:
            # Check if class name only, return if is
            if Path(model_ref).stem == str(model_ref):
                return str(model_ref)
            # Otherwise error
            raise TypeError(
                f"Unable to serialise model_ref; "
                f"expected python file path Path or model name str, "
                f"got {type(model_ref)} with value {model_ref}"
            ) from ae

    @staticmethod
    def load_model_ref(value: str) -> Union[Path, str]:
        """Deserialize the model_ref value.

        Used for deserialization of BitfountModelReference.
        """
        try:
            new_value = Path(value).expanduser()
            if new_value.stem == str(new_value):  # i.e. is just a class name
                return str(value)
            return new_value
        except TypeError:
            return str(value)


def _combine_dict_helper(
    cls: Any, item: Any, fields_dict: _JSONDict, nested_fields: _JSONDict
) -> Tuple[_JSONDict, _JSONDict]:
    """Helper function for bf_combine_load and _dump.

    Used to get the nested and unnested fields from the `item` class.
    """
    if hasattr(item, "fields_dict"):
        for k, v in item.fields_dict.items():
            if k not in fields_dict:
                fields_dict[k] = v
        for k, v in item.nested_fields.items():
            if k not in nested_fields:
                nested_fields[k] = v
    if hasattr(item, "optional_nested") and item.optional_nested is not None:
        if hasattr(cls, "optional_nested") and cls.optional_nested is not None:
            aux = [v for v in item.optional_nested if v not in cls.optional_nested]
            cls.optional_nested.extend(aux)
        else:
            cls.optional_nested = item.optional_nested.copy()
    return fields_dict, nested_fields


# Methods for loading the schema

# In bf_load, we take a dictionary which we convert to a schema using the
# `_dict_to_schema` function. For each item provided in to the
# `_dict_to_schema` function we also have to loop through the registers
#  given to make sure we load all attributes of the parent classes,
#  which we do using `_bf_combine_dict_load`.


def bf_load(dct: _JSONDict, registry: Mapping[str, Any]) -> Any:
    """Method for deserializing an object."""
    # Get the schema given a dictionary with the fields.
    schema_cls = _dict_to_schema(dct, registry)
    # Get the schema class and load the schema
    myschema = schema_cls()
    schema_load = myschema.load(dct)
    # Make sure all fields and the schema are deleted to prevent
    # memory leak.
    del myschema

    return schema_load


def _dict_to_schema(
    dct: _JSONDict, registry: Mapping[str, type], depth: int = 0
) -> Any:
    """Converts a dictionary to a marshmallow schema."""
    if depth > 5:
        raise SchemaClassError("Cannot have more than depth 5 in serialisation")
    if dct:
        # Get the class by looking in the given registry for the class_name after
        # removing the `bitfount.` prefix if present. This is present only on protocols,
        # algorithms, aggregators and models.
        cls: Any = registry[dct["class_name"].split(".", 1)[-1]]
        # Load all nested and unnested attributes of the parent classes.
        unnested_fields, nested_fields = _bf_combine_dict_load(
            cls, cls.fields_dict.copy(), cls.nested_fields.copy(), registry
        )
        unnested_fields["class_name"] = fields.Str()
        nested_fields_aux = {}

        # For each nested item, go recursively through them and unpack
        # to only have unnested fields and then generate schemas for
        # all of them.
        for (k, sub_reg) in nested_fields.items():
            if hasattr(cls, "optional_nested") and cls.optional_nested is not None:
                # If the nested item is optional, we can skip the KeyError
                if k in cls.optional_nested:
                    try:
                        aux = {k: _dict_to_schema(dct[k], sub_reg, depth + 1)}
                    except KeyError:
                        continue
                else:
                    aux = {k: _dict_to_schema(dct[k], sub_reg, depth + 1)}
            else:
                cls.optional_nested = None
                aux = {k: _dict_to_schema(dct[k], sub_reg, depth + 1)}
            nested_fields_aux.update(aux)
        # Get the schema of the class
        return _get_marshmallow_schema(cls, unnested_fields, nested_fields_aux)
    else:
        return None


def _bf_combine_dict_load(
    cls: Any,
    fields_dict: _JSONDict,
    nested_fields: _JSONDict,
    registry: Mapping[str, Any],
) -> Tuple[_JSONDict, _JSONDict]:
    """Combine the nested and unnested fields from the subclasses.

    This method loops through the registry and checks if any of
    the modules are superclasses of the given class. This is
    done explicitly as some of the subclasses are not loaded
    properly in the federated setting. This way, it ensures
    that both nested and unnested fields are loaded from all
    the respective subclasses.

    Args:
        cls: the class for which we want the nested and unnested fields.
        fields_dict: the unnested fields dictionary.
        nested_fields: the nested fields dictionary.
        registry: the registry with the (possible) superclasses
    """
    # We need a special check
    # for subclasses of CNNModelStructure as it may
    # overrides the default layer value with the layer value defined in the
    # NeuralNetworkModelStructure.
    # Below we force it to take the default value of the CNNModelStructure,
    # if it has not been defined with the model.

    if issubclass(cls, CNNModelStructure):
        if "layers" not in cls.fields_dict:
            fields_dict["layers"] = [16, 32]

    # Loop through the registry in order to load all relevant
    # nested and unnested fields from the parent classes.
    for item in registry.values():
        if issubclass(cls, item):
            fields_dict, nested_fields = _combine_dict_helper(
                cls, item, fields_dict, nested_fields
            )
    return fields_dict, nested_fields
