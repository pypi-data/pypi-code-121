import copy
import json
from typing import List, Optional, Type

import jsonref
from django.db.models.fields import Field
from jsonschema_to_openapi.convert import convert as convert_to_openapi
from pydantic.error_wrappers import ValidationError as PydanticValidationError
from pydantic.main import BaseModel
from rest_framework.serializers import JSONField

__all__ = ["PydanticJsonFieldSerializer"]


class PydanticJsonFieldSerializer(JSONField, Field):
    """
    Serializer for serializing our custom PydanticJsonField.

    Provides annotations for both drf-spectacular and drf-yasg
    """

    class Meta:
        swagger_schema_fields: dict

    def __init__(
        self, *args, pydantic_models: Optional[List[Type[BaseModel]]] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.schema = self.__schema_information(pydantic_models)

        # Set schema for drf-spectacular
        self.coreapi_schema = convert_to_openapi(copy.deepcopy(self.schema))

        # Set schema for drf-yasg
        PydanticJsonFieldSerializer.Meta.swagger_schema_fields = self.schema

        self.pydantic_models = pydantic_models if pydantic_models else []

    def to_representation(self, value):
        value = super().to_representation(value)

        for model in self.pydantic_models:
            try:
                if isinstance(value, dict):
                    return json.loads(model.parse_obj(value).json())
                else:
                    return json.loads(model.parse_raw(value).json())
            except PydanticValidationError:
                pass

    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        for model in self.pydantic_models:
            try:
                parsed_json = model.parse_obj(data)
                return json.loads(parsed_json.json())
            except PydanticValidationError:
                pass

        self.fail("invalid")

    def __schema_field_from_pydantic(self, pydantic_model: Type[BaseModel]) -> dict:
        schema = dict(jsonref.loads(pydantic_model.schema_json()))

        if "definitions" in schema:
            schema.pop("definitions")

        return schema

    def __schema_information(
        self, pydantic_models: Optional[List[Type[BaseModel]]]
    ) -> dict:
        """
        Returns a JSON schema that is used for representing the potential values of this field
        """

        if pydantic_models is None or pydantic_models.__len__() == 0:
            schema_information = {"type": "object"}

        elif pydantic_models.__len__() > 1:
            schema_information = {
                "anyOf": [
                    self.__schema_field_from_pydantic(model)
                    for model in pydantic_models
                ]
            }
        else:
            schema_information = self.__schema_field_from_pydantic(pydantic_models[0])

        return schema_information


try:
    from drf_spectacular.extensions import OpenApiSerializerFieldExtension

    class PydanticJsonFieldSerializerExtension(OpenApiSerializerFieldExtension):
        target_class = PydanticJsonFieldSerializer

        def map_serializer_field(self, auto_schema, direction):
            return self.target.schema or {"type": "object"}

except Exception:
    pass
