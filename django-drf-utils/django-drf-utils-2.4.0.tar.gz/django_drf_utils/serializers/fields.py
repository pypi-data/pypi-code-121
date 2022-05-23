from enum import Enum
from typing import Iterable

from rest_framework import serializers
from django_drf_utils.serializers.utils import DetailedValidationError


# TODO DRF contribution
def EnumChoiceField(choices: Iterable[Enum], use_enum: bool = False, **kwargs):
    if not use_enum:
        return serializers.ChoiceField(
            choices=[enum.name for enum in choices], **kwargs
        )

    enum_by_value = {e.value: e for e in choices}

    class _EnumChoiceField(serializers.Field):
        def to_representation(self, value):
            return value.name

        def to_internal_value(self, data):
            try:
                return enum_by_value[data]
            except KeyError as e:
                raise DetailedValidationError(
                    f"Invalid value: {data}", field=self.field_name
                ) from e

    return _EnumChoiceField(**kwargs)
