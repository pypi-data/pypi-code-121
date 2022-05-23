from typing import Any, Dict, List, Type
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.serializers import Serializer, ValidationError
from rest_framework import serializers


def get_request_username(serializer: Serializer) -> AbstractUser:
    return serializer.context["request"].user


class DetailedValidationError(ValidationError):
    def __init__(self, detail, field="detail"):
        super().__init__({field: detail}, code="invalid")


# TODO DRF contribution
def update_related_fields(
    instance: models.Model,
    related_serializer: Type[serializers.ModelSerializer],
    data: List[Dict[str, Any]],
):
    # pylint: disable=protected-access
    instance_name = instance._meta.model_name
    meta = related_serializer.__dict__["Meta"]
    related_model = meta.model
    # Read-only fields are NOT updatable
    fields = (
        set(meta.fields) - set(meta.read_only_fields)
        if hasattr(meta, "read_only_fields")
        else meta.fields
    )
    optional_fields_defaults = {
        f.name: "" if f.blank else None
        for f in related_model._meta.get_fields()
        if (f.name in fields) and (f.blank or f.null)
    }
    old = {
        tuple(getattr(model, field) for field in fields): model.id
        for model in related_model.objects.filter(**{instance_name: instance})
    }
    new = {
        tuple(
            obj[field] if field in obj else optional_fields_defaults[field]
            for field in fields
        )
        for obj in data
    }
    to_be_created = new - set(old)
    to_be_deleted = set(old) - new
    related_model.objects.bulk_create(
        [
            related_model(**{instance_name: instance}, **dict(zip(fields, values)))
            for values in to_be_created
        ]
    )
    related_model.objects.filter(pk__in=[old[obj] for obj in to_be_deleted]).delete()
