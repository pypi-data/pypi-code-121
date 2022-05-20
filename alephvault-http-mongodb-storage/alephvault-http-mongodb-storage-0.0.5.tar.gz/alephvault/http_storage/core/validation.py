from bson import ObjectId
from datetime import datetime
from cerberus import Validator, TypeDefinition
from ..types.method_handlers import MethodHandler, ItemMethodHandler
from .formats import DATETIME_FORMATS, DATE_FORMAT


class MongoDBEnhancedValidator(Validator):
    """
    This validator adds the following:
    - Registering types: objectid, method and item-method.
    - Default coercion of objectid using ObjectId.
    - Default coercion of date and datetime using custom formats.
    """

    types_mapping = {
        **Validator.types_mapping,
        "objectid": TypeDefinition("objectid", (ObjectId,), ()),
        "method": TypeDefinition("method", (MethodHandler,), ()),
        "item-method": TypeDefinition("item-method", (ItemMethodHandler,), ()),
    }

    def _normalize_coerce_str2date(self, value):
        """
        Coerces a date from a string in a %Y-%m-%d format.
        :param value: The string value to coerce.
        :return: The coerced date.
        """

        return datetime.strptime(value, DATE_FORMAT).date()

    def _normalize_coerce_str2datetime(self, value):
        """
        Coerces a datetime from a string in one of the available formats.
        :param value: The string value to coerce.
        :return: The coerced date.
        """

        for format in DATETIME_FORMATS:
            try:
                return datetime.strptime(value, format)
            except ValueError:
                continue
        raise ValueError(f"time data '{value}' does not match any of the available formats")

    @classmethod
    def apply_default_coercers(cls, schema, tracked=None):
        """
        In-place modifies a schema to add the default coercers to the input
        documents before validation. This method should be called only once
        per schema.
        :param schema: The schema to in-place modify and add the coercers.
        :param tracked: The already-tracked levels for this schema.
        """

        # Circular dependencies are ignored - they are already treated.
        if tracked is None:
            tracked = set()
        schema_id = id(schema)
        if schema_id in tracked:
            return

        if 'coerce' not in schema:
            type_ = schema.get('type')
            if type_ == "objectid":
                schema['coerce'] = ObjectId
            elif type_ == "date":
                schema['coerce'] = 'str2date'
            elif type_ == "datetime":
                schema['coerce'] = 'str2datetime'
        # We iterate over all the existing dictionaries to repeat this pattern.
        # For this we also track the current schema, to avoid circular dependencies.
        tracked.add(schema_id)
        for sub_schema in schema.values():
            if isinstance(sub_schema, dict):
                cls.apply_default_coercers(sub_schema, tracked)
        tracked.remove(schema_id)
