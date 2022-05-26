from typing import List

from django.contrib.contenttypes.models import ContentType
from django.db import ProgrammingError
from django.db.models import Model, QuerySet
from rest_framework.serializers import ChoiceField


def serializer_choice_field_for_polymorphic_ctype_id(
    models: List[Model], app_label: str
) -> ChoiceField:
    """
    Provides a choice field for polymorphic ctype id fields based on a given set of models
    """

    try:
        content_types: QuerySet[ContentType] = ContentType.objects.filter(
            app_label=app_label,
            model__in=[model._meta.model_name for model in models],
        )

        return ChoiceField(
            choices=[(type.pk, type.model) for type in content_types.all()]
        )
    except ProgrammingError:
        return ChoiceField(choices=[])


__all__ = ["serializer_choice_field_for_polymorphic_ctype_id"]
