from typing import List, Optional, Type

from django.core.exceptions import ValidationError
from django.db.models import JSONField
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError


class PydanticJsonField(JSONField):
    def __init__(
        self, *args, pydantic_models: Optional[List[Type[BaseModel]]] = None, **kwargs
    ):
        self.pydantic_models: List[Type[BaseModel]] = (
            pydantic_models if pydantic_models else []
        )

        kwargs_to_pass = kwargs
        kwargs_to_pass.pop("pydantic_models", None)

        super().__init__(*args, **kwargs_to_pass)

    def _validate_schema(self, value):
        # Disable validation when migrations are faked
        if self.model.__module__ == "__fake__":
            return True

        validation_errors = []

        for model in self.pydantic_models:
            try:
                if isinstance(value, str):
                    model.parse_raw(value)
                else:
                    model.parse_obj(value)

                # Unset validation errors on successful parsing and break loop
                validation_errors = []
                break

            except PydanticValidationError as exc:
                validation_errors.append(
                    f"JSON does not fit Pydantic model {model.__name__} {format(exc)}"
                )

        if validation_errors.__len__() > 0:
            raise ValidationError(validation_errors)

        return value

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        self._validate_schema(value)

    def pre_save(self, model_instance, add):
        value = super().pre_save(model_instance, add)
        if value and not self.null:
            self._validate_schema(value)
        return value
